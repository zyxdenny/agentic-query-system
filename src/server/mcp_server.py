import pandas as pd
import sqlite3
import json
from mcp.server.fastmcp import FastMCP

root = "./"


# Load Table_feeds_v2.csv
DB_FILE = "cameras.db"
conn = sqlite3.connect(DB_FILE)
df = pd.read_csv(f"{root}/camera-raw-data/Table_feeds_v2.csv")
df.to_sql("Table_feeds_v2", conn, if_exists="replace", index=False)
conn.close()

# Load encoder_params.json
with open(f"{root}/camera-raw-data/encoder_params.json", "r") as f:
    encoder_params = json.load(f)

# Load decoder_params.json
with open(f"{root}/camera-raw-data/decoder_params.json", "r") as f:
    decoder_params = json.load(f)

# Load encoder_schema.json
with open(f"{root}/camera-raw-data/encoder_schema.json", "r") as f:
    encoder_schema = json.load(f)

# Load decoder_schema.json
with open(f"{root}/camera-raw-data/decoder_schema.json", "r") as f:
    decoder_schema = json.load(f)


mcp = FastMCP("Cameras SQL queries, encoder and decoder information")

def run_query(query: str) -> str:
    """
    Run a SQL query on Table_feeds_v2
    """
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
            return f"Query executed successfully: {query}"
    except Exception as e:
        return f"Error when executing `{query}`: {e}"
    finally:
        conn.close()


@mcp.tool()
def sql_query(query: str):
    return run_query(query)


@mcp.tool()
def get_field_encoder_param(field: str):
    """
    get a field in encoder_params
    """
    value = encoder_params.get(field)
    if value is None:
        return f"Error: {field} is not in encoder paramerters"
    return value


@mcp.tool()
def get_field_decoder_param(field: str):
    """
    get a field in decoder_params
    """
    value = decoder_params.get(field)
    if value is None:
        return f"Error: {field} is not in decoder paramerters"
    return value


@mcp.tool()
def get_field_encoder_schema(field: str):
    """
    get a field of properties in encoder_schema
    """
    value = encoder_params.get("properties").get(field)
    if value is None:
        return f"Error: {field} is not in encoder schema"
    return value


@mcp.tool()
def get_field_decoder_schema(schema: str):
    """
    get a field of properties in decoder_schema
    """
    value = decoder_params.get("properties").get(field)
    if value is None:
        return f"Error: {field} is not in decoder schema"
    return value


@mcp.tool()
def get_required_fields_encoder():
    """
    get the required fields encoder parameters must have
    """
    required = encoder_schema.get("required")
    return f"The required fields are {required}"


@mcp.tool()
def get_required_fields_decoder():
    """
    get the required fields decoder parameters must have
    """
    required = decoder_schema.get("required")
    return f"The required fields are {required}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
