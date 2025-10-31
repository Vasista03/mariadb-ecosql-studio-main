"""
VannaMariaDB Wrapper — unified embedding + query system using MariaDB.
Supports multi-dataset vector tagging for:
  - training_data  → generic Q&A pairs
  - openflights    → schema + documentation + sample Q→SQL
"""

import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from vanna.base import VannaBase
from backend.openai_client import get_embedding, chat_openai
from backend.mariadb_utils import engine, init_vector_table, drop_vectors_by_type
from backend.config import VECTOR_TABLE

# Ensure vector table exists
init_vector_table()


class VannaMariaDB(VannaBase):
    def __init__(self):
        super().__init__(config=None)

    # ---------------- Abstract Implementations ----------------
    def system_message(self, message: str):
        return f"[SYSTEM] {message}"

    def user_message(self, message: str):
        return f"[USER] {message}"

    def assistant_message(self, message: str):
        return f"[ASSISTANT] {message}"

    # ---------- Embeddings & Prompt ----------
    def generate_embedding(self, text: str):
        return get_embedding(text)

    def submit_prompt(self, prompt, **kwargs):
        """Unified chat interface — compatible with new OpenAI API."""
        if isinstance(prompt, list):
            prompt = "\n".join(str(p).strip() for p in prompt if p)
        prompt = str(prompt).strip()
        try:
            return chat_openai(prompt)
        except Exception as e1:
            try:
                return chat_openai(
                    prompt + "\nReturn only the SQL query (single line)."
                )
            except Exception as e2:
                raise RuntimeError(f"LLM failure: {e2}")

    # ---------- Vector Database Operations ----------
    def _insert_vector(self, vtype, content, dataset="default"):
        """Insert a vector row with dataset tag."""
        emb = self.generate_embedding(content)
        vid = f"{vtype}-{np.random.randint(1e9)}"
        with engine.connect() as conn:
            conn.execute(
                text(
                    f"""
                    INSERT INTO {VECTOR_TABLE} (id, content, type, embedding, dataset)
                    VALUES (:id, :content, :type, :embedding, :dataset)
                """
                ),
                {
                    "id": vid,
                    "content": content,
                    "type": vtype,
                    "embedding": json.dumps(emb),
                    "dataset": dataset,
                },
            )
            conn.commit()
        return f"{vtype} added to dataset '{dataset}'."

    def _query_vectors(self, query, vtype, top_k=3, dataset=None):
        """Retrieve vectors filtered by dataset + type using cosine similarity."""
        q_emb = np.array(self.generate_embedding(query))
        sql = f"SELECT * FROM {VECTOR_TABLE} WHERE type = '{vtype}'"
        if dataset:
            sql += f" AND dataset = '{dataset}'"

        with engine.connect() as conn:
            df = pd.read_sql(sql, conn)

        if df.empty:
            return []

        df["embedding_list"] = df["embedding"].apply(lambda e: np.array(json.loads(e)))
        df["similarity"] = df["embedding_list"].apply(
            lambda emb: float(
                np.dot(q_emb, emb)
                / (np.linalg.norm(q_emb) * np.linalg.norm(emb) + 1e-10)
            )
        )
        return (
            df.sort_values("similarity", ascending=False)
            .head(top_k)["content"]
            .tolist()
        )

        # ---------- Training Data Management (Required by VannaBase) ----------

    def get_training_data(self, **kwargs):
        """Retrieve all rows from the vector store (for inspection or export)."""
        with engine.connect() as conn:
            return pd.read_sql(f"SELECT * FROM {VECTOR_TABLE}", conn)

    def remove_training_data(self, id: str, **kwargs) -> bool:
        """Remove a specific embedding entry by ID."""
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM {VECTOR_TABLE} WHERE id = :id"), {"id": id})
            conn.commit()
        return True

    # ---------- Public API ----------
    def add_ddl(self, ddl, dataset="default"):
        return self._insert_vector("ddl", ddl, dataset)

    def add_documentation(self, doc, dataset="default"):
        return self._insert_vector("documentation", doc, dataset)

    def add_question_sql(self, q, sql, dataset="default"):
        combined = f"Question: {q}\nSQL: {sql}"
        return self._insert_vector("question_sql", combined, dataset)

    def get_related_ddl(self, q, dataset=None):
        return self._query_vectors(q, "ddl", dataset=dataset)

    def get_related_documentation(self, q, dataset=None):
        return self._query_vectors(q, "documentation", dataset=dataset)

    def get_similar_question_sql(self, q, top_k=5, dataset=None):
        return self._query_vectors(q, "question_sql", top_k, dataset)

    def run_sql(self, sql: str):
        return pd.read_sql_query(sql, engine)

    # ---------- Core Ask ----------
    def ask(self, question: str, dataset="openflights"):
        """Use only OpenFlights context when generating queries."""
        related = (
            self.get_related_ddl(question, dataset=dataset)
            + self.get_related_documentation(question, dataset=dataset)
            + self.get_similar_question_sql(question, dataset=dataset)
        )
        context = "\n\n".join(related)

        with engine.connect() as conn:
            tables = [r[0] for r in conn.execute(text("SHOW TABLES")).fetchall()]
            schema_details = []
            for t in tables:
                create_stmt = conn.execute(text(f"SHOW CREATE TABLE {t}")).fetchone()[1]
                schema_details.append(create_stmt)
            schema_context = "\n\n".join(schema_details)

        prompt = f"""
You are a MariaDB SQL expert.
Use only the schema and examples below to generate a single SQL query in MariaDB syntax.

Schema:
{schema_context}

Context (from dataset: {dataset}):
{context}

Question:
{question}

Return only the SQL query (no explanation).
"""
        return self.submit_prompt(prompt)


# =====================================================
# 🔹 Training utilities
# =====================================================
def drop_training_vectors(vn, types=("ddl", "documentation", "question_sql")):
    """Drop all training-related vector entries."""
    drop_vectors_by_type(types)
    print(f"✅ Dropped vector types: {types}")


def train_from_mariadb_training_table(vn, training_table_name="training_pairs"):
    """Train model on generic Q&A data from training DB (for structure learning)."""
    with engine.connect() as conn:
        res = conn.execute(text(f"SHOW TABLES LIKE '{training_table_name}'")).fetchall()
        if not res:
            print(f"⚠️ Training table '{training_table_name}' not found. Skipping.")
            return
        df = pd.read_sql(f"SELECT * FROM {training_table_name}", conn)

    added = 0
    for _, row in df.iterrows():
        q = str(row.get("question", "")).strip()
        sql = str(row.get("sql", "") or row.get("answer", "")).strip()
        if q and sql:
            vn.add_question_sql(q, sql, dataset="training_data")
            added += 1
    print(f"✅ Added {added} Q&A examples from '{training_table_name}'.")


def train_from_openflights_schema(vn):
    """Train embeddings from OpenFlights schema and add domain-specific examples."""
    with engine.connect() as conn:
        tables = [r[0] for r in conn.execute(text("SHOW TABLES")).fetchall()]

    for t in tables:
        ddl = pd.read_sql(text(f"SHOW CREATE TABLE {t}"), engine).iloc[0, 1]
        vn.add_ddl(ddl, dataset="openflights")

        cols = pd.read_sql(text(f"SHOW COLUMNS FROM {t}"), engine)
        col_info = ", ".join(
            [f"{row['Field']} ({row['Type']})" for _, row in cols.iterrows()]
        )
        vn.add_documentation(f"Table '{t}' columns: {col_info}", dataset="openflights")

    # Add OpenFlights-specific Q&A
    examples = [
        (
            "Which country has the most airports?",
            "SELECT country, COUNT(*) AS airport_count FROM airport GROUP BY country ORDER BY airport_count DESC LIMIT 1;",
        ),
        ("List all active airlines.", "SELECT * FROM airlines WHERE active = 'Y';"),
        (
            "Top 10 routes by number of stops.",
            "SELECT airline, source_airport, destination_airport, stops FROM routes ORDER BY stops DESC LIMIT 10;",
        ),
        (
            "List airports in India with IATA codes.",
            "SELECT name, city, iata FROM airport WHERE country = 'India';",
        ),
        (
            "How many routes per airline?",
            "SELECT airline_id, COUNT(*) AS route_count FROM routes GROUP BY airline_id ORDER BY route_count DESC;",
        ),
    ]
    for q, s in examples:
        vn.add_question_sql(q, s, dataset="openflights")

    print(f"✅ Added {len(examples)} OpenFlights Q→SQL examples and schema docs.")
