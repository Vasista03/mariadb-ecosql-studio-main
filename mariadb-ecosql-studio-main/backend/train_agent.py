# backend/train_agent.py
"""
Training entry point for VannaMariaDB Agent.
This trains the AI model on:
  1. Generic SQL Q&A pairs from your training database (dataset='training_data')
  2. OpenFlights schema and documentation (dataset='openflights')
"""

from backend.vanna_train import (
    VannaMariaDB,
    drop_training_vectors,
    train_from_mariadb_training_table,
    train_from_openflights_schema
)
from backend.mariadb_utils import engine
from sqlalchemy import text


if __name__ == "__main__":
    print("🚀 Starting fresh training...")

    from sqlalchemy import inspect

def ensure_dataset_column():
    with engine.connect() as conn:
        insp = inspect(engine)
        cols = [col['name'] for col in insp.get_columns('vector_store')]
        if 'dataset' not in cols:
            print("⚙️ Adding missing 'dataset' column to vector_store...")
            conn.execute(text("ALTER TABLE vector_store ADD COLUMN dataset VARCHAR(100) DEFAULT 'default';"))
            conn.commit()
        else:
            print("✅ Verified: 'dataset' column exists in vector_store")

# --- Force schema refresh ---
    ensure_dataset_column()
    engine.dispose()  # 🔥 Force SQLAlchemy to drop all cached connections

    # Initialize agent
    vn = VannaMariaDB()

    # ================================================
    # 1️⃣ Drop existing vectors (for clean retrain)
    # ================================================
    try:
        drop_training_vectors(vn, types=("ddl", "documentation", "question_sql"))
    except Exception as e:
        print(f"⚠️ Could not drop existing vectors: {e}")

    # ================================================
    # 2️⃣ Train from your internal 'training_pairs' table
    # ================================================
    try:
        train_from_mariadb_training_table(vn, training_table_name="training_pairs")
    except Exception as e:
        print(f"⚠️ Training data phase skipped: {e}")

    # ================================================
    # 3️⃣ Train on OpenFlights schema
    # ================================================
    try:
        train_from_openflights_schema(vn)
    except Exception as e:
        print(f"⚠️ OpenFlights schema training failed: {e}")

    # ================================================
    # ✅ Summary
    # ================================================
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM vector_store")).fetchone()[0]
    print(f"\n✅ Training completed successfully! Total embeddings: {total}")
