import pandas as pd
import sqlite3
import glob
from mcp.server.fastmcp import FastMCP

root = "./"
DB_FILE = "cameras.db"
conn = sqlite3.connect(DB_FILE)

df = pd.read_csv(f"{root}/camera-raw-data/Table_feeds_v2.csv")
df.to_sql("Table_feeds_v2", conn, if_exists="replace", index=False)

conn.close()

mcp = FastMCP("Cameras SQL queries")

def run_query(query: str) -> str:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(query)
        if cur.description:
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            output = [", ".join(columns)]
            for row in rows:
                output.append(", ".join(str(v) for v in row))
            return "\n".join(output)
        else:
            conn.commit()
            return f"Query executed successfully: {query}\n"
    except Exception as e:
        return f"Error when executing `{query}`: {e}\nDB_FILE is: {DB_FILE}\n"
    finally:
        conn.close()


@mcp.tool()
def sql_query(query: str):
    return run_query(query)


# @mcp.tool()
# def list_tables() -> str:
#     """List all tables in the SQLite database."""
#     conn = sqlite3.connect(DB_FILE)
#     cur = conn.cursor()
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = [row[0] for row in cur.fetchall()]
#     conn.close()
#     return ", ".join(tables)
# 
# 
# @mcp.tool()
# def describe_table(table: str) -> str:
#     """Show schema for a given table."""
#     conn = sqlite3.connect(DB_FILE)
#     cur = conn.cursor()
#     cur.execute(f"PRAGMA table_info({table});")
#     rows = cur.fetchall()
#     conn.close()
#     return "\n".join([f"{r[1]} ({r[2]})" for r in rows])


if __name__ == "__main__":
    mcp.run(transport="stdio")
