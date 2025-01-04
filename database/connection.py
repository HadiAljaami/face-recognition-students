# Step 1: Database Connection (connection.py)
# Located in database/connection.py
import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    try:
        conn = psycopg.connect(
            "postgresql://postgres:1234@localhost:5432/vectors_db",
            row_factory=dict_row
        )
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        raise

#from psycopg_pool import ConnectionPool