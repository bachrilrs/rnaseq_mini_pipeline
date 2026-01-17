import psycopg2
from psycopg2 import sql
import os 
from dotenv import load_dotenv

def setup_database() -> None:
    """
    Set up the PostgreSQL database.

    
    """
    env = load_dotenv()  # Load environment variables from .env file
    
    return psycopg2.connect(
        database = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
        host = os.getenv("POSTGRES_HOST"),  # Assuming the database host is 'db' in the Docker network
        port = os.getenv("POSTGRES_PORT")
    )

def create_tables(conn) -> None:
    """ Create necessary tables in the database.
    """
    cursor = conn.cursor()
    cur = conn.cursor()

    with open ("./sql/create_tables.sql", 'r') as f:
        cur.execute(f.read())
    conn.commit()
    cur.close
    conn.close()
    print('Tables created successfully.')


    # SEPARATE THE CONNECTION AND USAGE LOGIC

    # TODO

    
    # cursor = conn.cursor()

    # cursor.execute("SELECT * FROM run;")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
    
def insert_postgresql_db():
    conn = setup_database()
    create_tables(conn)

    # TODO: Add logic to insert data into tables


