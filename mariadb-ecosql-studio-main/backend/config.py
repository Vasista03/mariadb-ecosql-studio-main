
# backend/config.py
"""
Configuration values. Update MARIADB_URI to match your environment.
"""
import os

# Example: mariadb+pymysql://root:MyPass%40123@localhost:3306/train_database
MARIADB_URI = os.getenv("MARIADB_URI", "mariadb+pymysql://root:password@localhost:3306/your_database")
VECTOR_TABLE = os.getenv("VECTOR_TABLE", "vector_store")

# OpenAI (preferred) config (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "apikey")  # or set in your environment
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")  # change as needed

# Fallback local sentence-transformers model (used if OPENAI_API_KEY not present)
LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
