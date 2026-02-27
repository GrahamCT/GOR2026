import os
from dotenv import load_dotenv
import pyodbc

load_dotenv() 


CONN_STRING = os.getenv("GOR_CONN_STRING")


def getConstring(con):
    if con =='GOR': 
        return os.getenv("GOR_CONN_STRING")
    
    if con=='TUG':
        return os.getenv("TUG_CONN_STRING")

def dal(typeExOrFetch, query: str, params: tuple=None, cons:str = 'GOR'):
    # type=0 execute, 1=fetch all

    constring = getConstring(cons.upper())

    if typeExOrFetch==0: #generic execute
        try:
            with pyodbc.connect(constring) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return "ok"
        except Exception as e:
            print(f"Database execution error: {e}")
            return "error"
    elif typeExOrFetch ==1:
        with pyodbc.connect(constring) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        if not rows:
            return None

        # Convert rows to list of dicts
        results = [dict(zip(columns, row)) for row in rows]
        return results  

  
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
