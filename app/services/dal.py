import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()


CONN_STRING = os.getenv("GOR_CONNECTION")


def dal(typeEx0_OrFetch1, query: str, params: tuple=None):
    # type=0 execute, 1=fetch all

    if typeEx0_OrFetch1==0: #generic execute
        try:
            with pyodbc.connect(CONN_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return "ok"
        except Exception as e:
            print(f"Database execution error: {e}")
            return "error"

    elif typeEx0_OrFetch1 ==1:
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

    elif typeEx0_OrFetch1 == 2: #generic execute with return row
         with pyodbc.connect(CONN_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                row = cursor.fetchone()
                conn.commit()

                return row



def exec_sp(query: str, params: tuple = None):
    """Execute a stored procedure and return a single value from the result."""
    with pyodbc.connect(CONN_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        conn.commit()
    if row:
        return row[0]
    return None


def generic_execute(query: str, params: tuple = None, constring = CONN_STRING):

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

def generic_execute_return(query: str, params: tuple = None):
    with pyodbc.connect(CONN_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        while cursor.description is None:
            if not cursor.nextset():
                return None
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        conn.commit()
    if not row:
        return None
    return dict(zip(columns, row))



def generic_fetch_multiple_datasets(query: str, params: tuple = None):
    results = {}
    set_index = 1

    with pyodbc.connect(CONN_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        while True:
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                results[f"result_{set_index}"] = [
                    dict(zip(columns, row))
                    for row in rows
                ]

                set_index += 1

            if not cursor.nextset():
                break

    return results or None
