"""Database setup and connection."""

import os
import psycopg2
import pandas as pd


def connect_database():
    """Connect to PostgreSQL database."""
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 5432))
    user = os.getenv('DB_USER', 'rnaseq_user')
    password = os.getenv('DB_PASSWORD', 'rnaseq_password') 
    database = os.getenv('DB_NAME', 'rnaseq_db')
    
    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,  
        database=database,
        connect_timeout=10
    )


def create_tables(conn):
    """Drop old tables and create fresh schema."""
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS qc_metrics CASCADE")
        cur.execute("DROP TABLE IF EXISTS samples CASCADE")
        cur.execute("DROP TABLE IF EXISTS runs CASCADE")
        
        cur.execute("""
            CREATE TABLE samples (
                sample_id SERIAL PRIMARY KEY,
                sample_name VARCHAR(255),
                condition VARCHAR(100),
                replicate VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE qc_metrics (
                metric_id SERIAL PRIMARY KEY,
                sample_name VARCHAR(255),
                total_reads BIGINT,
                alignment_rate FLOAT,
                mean_quality FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE runs (
                run_id SERIAL PRIMARY KEY,
                pipeline_version VARCHAR(50),
                status VARCHAR(50),
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✓ Tables created")


def insert_qc_data(conn, samples_df, counts_df):
    """Insert QC metrics."""
    with conn.cursor() as cur:
        if samples_df is not None and len(samples_df) > 0:
            for _, row in samples_df.iterrows():
                cur.execute(
                    "INSERT INTO samples (sample_name, condition, replicate) VALUES (%s, %s, %s)",
                    (str(row.iloc[0]), str(row.get('condition', '')), str(row.get('replicate', '')))
                )
            conn.commit()
            print(f"✓ Inserted {len(samples_df)} samples")
        
        if counts_df is not None and len(counts_df) > 0:
            for col in counts_df.columns:
                cur.execute(
                    "INSERT INTO qc_metrics (sample_name, total_reads) VALUES (%s, %s)",
                    (col, int(counts_df[col].sum()))
                )
            conn.commit()
            print(f"✓ Inserted {len(counts_df.columns)} metrics")


def run_database():
    """Main database setup."""
    try:
        conn = connect_database()
        print("✓ Database connected")
        
        create_tables(conn)
        
        # Load data
        samples_df = None
        counts_df = None
        
        if os.path.exists('data/samples.csv'):
            samples_df = pd.read_csv('data/samples.csv')
        
        if os.path.exists('data/counts.csv'):
            counts_df = pd.read_csv('data/counts.csv', index_col=0)
        
        if samples_df is not None or counts_df is not None:
            insert_qc_data(conn, samples_df, counts_df)
        
        conn.close()
        print("✓ Database setup complete")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def main():
    """Entry point."""
    run_database()


if __name__ == '__main__':
    main()