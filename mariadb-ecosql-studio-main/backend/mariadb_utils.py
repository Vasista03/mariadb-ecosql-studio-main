# backend/mariadb_utils.py
"""
MariaDB utils: engine creation, ensure vector table exists, helper functions.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from backend.config import MARIADB_URI, VECTOR_TABLE

# Use future=True style engine for SQLAlchemy 1.4+
engine = create_engine(MARIADB_URI, pool_pre_ping=True)

def init_vector_table():
    """Create vector table if not exists (id primary key, content/text, type, embedding JSON/text)."""
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {VECTOR_TABLE} (
        id VARCHAR(128) NOT NULL PRIMARY KEY,
        content LONGTEXT,
        type VARCHAR(64),
        embedding LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()

def drop_vectors_by_type(types):
    """Delete all vectors of given types (list or string) using MariaDB syntax."""
    if isinstance(types, str):
        types = [types]

    with engine.connect() as conn:
        for t in types:
            # ✅ Safe, explicit SQL compatible with MariaDB / HeidiSQL
            delete_query = text(f"DELETE FROM {VECTOR_TABLE} WHERE type = '{t}'")
            conn.execute(delete_query)

        conn.commit()
    print(f"✅ Dropped vector types: {tuple(types)}")

