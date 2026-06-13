import psycopg2

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user='annamalai238',
        password='annamalai238',
        host='127.0.0.1',
        port='5432'
    )
    print("SUCCESS: Connected successfully using username: 'annamalai238' and password 'annamalai238'!")
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
