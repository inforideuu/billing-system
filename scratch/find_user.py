import psycopg2

usernames = ['postgres', 'annam', 'annamalai', 'root']

for user in usernames:
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password='annamalai238',
            host='localhost',
            port='5432'
        )
        print(f"SUCCESS: Connected successfully using username: '{user}' and password 'annamalai238'!")
        conn.close()
        break
    except Exception as e:
        err_msg = str(e).strip()
        print(f"Failed for user '{user}': {err_msg}")
