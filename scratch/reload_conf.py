import psycopg2

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        host='127.0.0.1',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Reload the configuration files
    cursor.execute("SELECT pg_reload_conf();")
    print("SUCCESS: Triggered pg_reload_conf() successfully. PostgreSQL has reloaded the secure pg_hba.conf file!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Failed to reload config: {e}")
