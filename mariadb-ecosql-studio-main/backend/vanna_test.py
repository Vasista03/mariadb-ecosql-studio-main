# backend/test_runner.py
"""
Test Runner for OpenFlights Dataset
-----------------------------------
This script:
✅ Loads the trained VannaMariaDB model.
✅ Runs a list of test questions (OpenFlights-focused).
✅ Prints generated SQL + sample query output.
✅ Handles empty or invalid SQL gracefully.
"""

from backend.vanna_train import VannaMariaDB
from backend.mariadb_utils import engine
from sqlalchemy import text
import pandas as pd

# ---------------------------------------------------------------
# 🧠 TEST QUESTIONS (OpenFlights domain)
# ---------------------------------------------------------------
TEST_QUESTIONS = [
    "Which country has the most airports?",
    "List all active airlines.",
    "Show top 10 routes by number of stops.",
    "List all airports in India with their IATA codes.",
    "How many planes are listed in the planes table?",
    "Which countries have more than 100 airports?",
    "Show all routes that connect airports in the USA.",
    "Get the number of routes per airline.",
    "Which airports have altitude greater than 5000 feet?",
]

# ---------------------------------------------------------------
# 🚀 TEST RUNNER
# ---------------------------------------------------------------
def run_tests():
    vn = VannaMariaDB()
    print("\n🚀 Starting OpenFlights Query Tests...\n")
    results = []

    for idx, q in enumerate(TEST_QUESTIONS, start=1):
        print(f"\n{'='*80}")
        print(f"🧠 [{idx}/{len(TEST_QUESTIONS)}] Question:")
        print(f"👉 {q}")

        # Generate SQL from the OpenFlights dataset context only
        try:
            sql = vn.ask(q, dataset="openflights")
        except Exception as e:
            print(f"⚠️ LLM generation error: {e}")
            results.append((q, None, f"LLM Error: {e}"))
            continue

        # Show SQL
        print("\n💡 Generated SQL:\n", sql if sql else "(EMPTY/NULL)")

        # If no SQL generated, skip execution
        if not sql or not sql.strip():
            print("⚠️ No SQL produced — skipping execution.")
            results.append((q, sql, "EMPTY"))
            continue

        # Execute SQL
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(text(sql), conn)
            if not df.empty:
                print("\n✅ Sample Output (Top 5 rows):")
                print(df.head(5).to_string(index=False))
                results.append((q, sql, "OK", df))
            else:
                print("\nℹ️ Query executed successfully, but returned no rows.")
                results.append((q, sql, "EMPTY_RESULT"))
        except Exception as e:
            print("⚠️ SQL Execution Error:", repr(e))
            results.append((q, sql, f"ERROR: {e}"))

    print("\n" + "="*80)
    print("✅ TEST SUMMARY")
    for q, sql, status, *rest in results:
        print(f"• {q[:50]:50s} → {status}")
    print("="*80)

    return results


# ---------------------------------------------------------------
# 🏁 MAIN ENTRY POINT
# ---------------------------------------------------------------
if __name__ == "__main__":
    run_tests()
