import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to the default 'postgres' database to check/create the target database
    connection = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='annamalai238',
        host='127.0.0.1',
        port='5432'
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    print("Connection Success!")
    
    with connection.cursor() as cursor:
        # Check if the database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'retail_billing_db';")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE retail_billing_db;")
            print("Database retail_billing_db created successfully.")
        else:
            print("Database retail_billing_db already exists.")
            
    connection.close()
except Exception as e:
    print(f"Connection Failure: {e}")

