# MariaDB EcoSQL Studio

Smarter Queries. Greener Insights.

## Features
- Natural Language → SQL via Vanna.AI
- Optimized queries using SQLGlot
- Carbon-aware metrics using MariaDB EXPLAIN
- Streamlit dashboards with Groq

## Folder Structure
See `mariadb-ecosql-studio/` for modules:
- `backend/` — FastAPI server
- `frontend/` — Streamlit app
- `database/` — MariaDB schema + seed

## Setup Instructions
1. Clone repo, create `.env`
2. Run MariaDB and execute `init_db.sql`
3. Install Python deps: `pip install -r requirements.txt`
4. Start: `bash run.sh`

Happy hacking 🚀
