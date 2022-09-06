# if database {DB_NAME} does not exist create it
import os
import time

import psycopg2

# establishing the connection
reconnect = 5
conn = None
while True:
    try:
        print("trying to connect to db...")
        conn = psycopg2.connect(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
        )
        break
    except Exception as e:
        print(e)
        print(f"reconnect: {reconnect}")
        time.sleep(1)
        reconnect -= 1
        if reconnect == 0:
            break

if conn is not None:
    conn.autocommit = True

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    print(f'{os.environ["DB_NAME"]}')
    try:
        # Creating a database
        cursor.execute(f'CREATE database {os.environ["DB_NAME"]}')
        print("Database created successfully........")
    # if the database already exist ignore
    except Exception:
        print("Database already there........")

    # Closing the connection
    conn.close()
else:
    print("failed to connect to db")

app_name = os.getenv("APP_NAME")
print("running migration for app :", app_name)
os.chdir(f"./{app_name}")
os.system("alembic upgrade head")
