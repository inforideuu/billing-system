import psycopg2

passwords = [
    'annamalai238',
    'Annamalai238',
    'annamalai2382',
    'Annamalai2382',
    'annamalai',
    'Annamalai',
    'postgres',
    'root',
    'admin',
    'annamalai@238',
    'Annamalai@238'
]

for pwd in passwords:
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=pwd,
            host='127.0.0.1',
            port='5432'
        )
        print(f"SUCCESS: Connected successfully to PostgreSQL using password: '{pwd}'!")
        conn.close()
        break
    except Exception as e:
        print(f"Failed for password '{pwd}': {e}")
