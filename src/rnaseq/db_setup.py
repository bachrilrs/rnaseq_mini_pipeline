import psycopg2
from psycopg2 import sql
import os , sys
import yaml
from dotenv import load_dotenv
import pandas as pd

load_dotenv()  # Load environment variables from .env file

def connect_database() -> None:
    """
    Set up the PostgreSQL database.
    """
    
    return psycopg2.connect(
        database = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
        host = os.getenv("POSTGRES_HOST", "db"),  # Assuming the database host is 'db' in the Docker network
        port = os.getenv("POSTGRES_PORT")
    )

def create_tables(conn) -> None:
    """ Create necessary tables in the database.
    """
    cur = conn.cursor()

    with open ("./sql/create_tables.sql", 'r') as f:
        sql_content = f.read()

        commands = sql_content.split(';')

        for command in commands:
            command = command.strip()
            if command:
                cur.execute(command)
    conn.commit() # python works with transactions , have to commit changes 
    cur.close()
    print('Tables created successfully.')

def insert_postgresql_db(con, csv_path, table_name, dataset_id, version, run_name) -> None:
    df = pd.read_csv(csv_path)
    
    # Safety: Ensure these are never None
    dataset_id = dataset_id or "Unknown_DS"
    version = version or "Unknown_version"
    run_name = run_name or f"Run_{dataset_id}"

    try:
        with con.cursor() as cur:
            # 1. Register the Run
            run_query = """
                INSERT INTO runs (run_name, pipeline_version, dataset_id) 
                VALUES (%s, %s, %s) RETURNING run_id
            """
            cur.execute(run_query, (run_name, version, dataset_id))
            active_run_id = cur.fetchone()[0]

            # 2. Add samples to 'samples' table if they don't exist (FK requirement)
            if 'sample_id' in df.columns:
                sample_query = "INSERT INTO samples (sample_id) VALUES (%s) ON CONFLICT (sample_id) DO NOTHING"
                for s_id in df['sample_id'].unique():
                    cur.execute(sample_query, (s_id,))

            # 3. Inject run_id for metrics
            df['run_id'] = active_run_id

            # 4. Filter columns
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
            db_columns = [row[0].lower() for row in cur.fetchall()]
            
            cols_to_use = [col for col in df.columns if col.lower() in db_columns]
            if cols_to_use:
                valid_df = df[cols_to_use].copy()
                valid_df = valid_df.where(pd.notnull(valid_df), None)
                
                cols = ", ".join(valid_df.columns)
                placeholders = ", ".join(["%s"] * len(valid_df.columns))

                if table_name == 'samples':
                    # This logic says: If the sample_id exists, just update the metadata
                    insert_query = f"""
                        INSERT INTO {table_name} ({cols}) 
                        VALUES ({placeholders})
                        ON CONFLICT (sample_id) DO UPDATE SET 
                            condition = EXCLUDED.condition,
                            geo_accession = EXCLUDED.geo_accession
                    """
                else:
                    # Standard insert for other tables
                    insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

                for _, row in valid_df.iterrows():
                    cur.execute(insert_query, tuple(row))
                
                con.commit()
                print(f"Successfully inserted into {table_name}")
            else:
                print(f"Skipping {table_name}: No matching columns found.")

    except Exception as e:
        con.rollback()
        print(f"Error during insertion into {table_name}: {e}")


# May be will be useful for interactive usage , i will leave it here
def requests(conn) -> None:
    """
    Main function to use the PostgreSQL database.
    """
    conn = connect_database()
    while True:
        sys.stdout.write("sql> ") # Prompt
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line or line.strip().lower() in ['quit']:
            break

        query = line.strip()
        if not query:
            continue

        try:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:  # If the query returns data
                    rows = cur.fetchall()
                    for row in rows:
                        print(row)
                conn.commit()  # Commit changes for INSERT/UPDATE/DELETE
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")

def run_database():
    dataset_id = os.getenv("DATASET_ID", "Unknown_Dataset")
    pipeline_version = os.getenv("PIPELINE_VERSION", "Unknown_Version")
    run_name = f"Run_{dataset_id}"
    csv_path = './output/GSE60450_qc/qc_table.csv'

    # establish connection
    conn = connect_database()

    try:
        
        print("Creating Database Tables")
        create_tables(conn)  

        # Samples table insertion
        print("Inserting data")
        insert_postgresql_db(conn, csv_path, 'samples', dataset_id, pipeline_version, run_name)
        # QC metrics insertion
        insert_postgresql_db(conn, csv_path, table_name='qc_metrics', dataset_id=dataset_id, 
                            version=pipeline_version, 
                            run_name=run_name)
    finally:
        conn.close()

def main():
    """
    Main function to run the RNA-seq QC pipeline based on a configuration file.
    Parameters: None
    """
    run_database()

if __name__ == "__main__":
    main()