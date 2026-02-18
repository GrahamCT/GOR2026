import os
from dotenv import load_dotenv
import pyodbc

load_dotenv() 

#get con string from env file
CONN_STRING = os.getenv("GOR_CONN_STRING")
# def generic_fetch_data(query: str, params: tuple = None):
#     with pyodbc.connect(CONN_STRING) as conn:
#         cursor = conn.cursor()
#         cursor.execute(query, params or ())
#         columns = [col[0] for col in cursor.description]
#         rows = cursor.fetchall()

#     if not rows:
#             return {"status": "ok"}
#     # Convert rows to list of dicts
#     results = [dict(zip(columns, row)) for row in rows]
#     return results

def generic_execute(query: str, params: tuple = None):
    try:
        with pyodbc.connect(CONN_STRING) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return "ok"
    except Exception as e:
        print(f"Database execution error: {e}")
        return "error"
    

def generic_fetch_data(query: str, params: tuple = None):
    with pyodbc.connect(CONN_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    if not rows:
        return None

    # Convert rows to list of dicts
    results = [dict(zip(columns, row)) for row in rows]
    return results    