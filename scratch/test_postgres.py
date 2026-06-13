import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_postgres():
    try:
        # Connect to the default 'postgres' database to check/create the target database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='annamalai238',
            host='127.0.0.1',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if the database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'retail_billing_db';")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE retail_billing_db;")
            print("Successfully created database 'retail_billing_db' in PostgreSQL.")
        else:
            print("Database 'retail_billing_db' already exists in PostgreSQL.")
            
        cursor.close()
        conn.close()
        print("PostgreSQL connection and setup check was SUCCESSFUL!")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")

if __name__ == "__main__":
    init_postgres()
