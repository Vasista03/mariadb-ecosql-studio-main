from sqlglot import parse_one
from sqlglot.optimizer import optimize


def optimize_sql_query(sql: str) -> str:
    try:
        return optimize(parse_one(sql)).sql(dialect="mariadb")
    except:
        return sql