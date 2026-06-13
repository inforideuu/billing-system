import psycopg2

try:
    # Connect in trust mode
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        host='127.0.0.1',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Update the password for postgres user to 'annamalai238'
    cursor.execute("ALTER USER postgres WITH PASSWORD 'annamalai238';")
    print("SUCCESS: Explicitly set password for user 'postgres' to 'annamalai238'!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Failed to set password: {e}")
