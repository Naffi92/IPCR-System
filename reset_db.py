import psycopg2
from decouple import config

try:
    conn = psycopg2.connect(
        dbname=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        port=config('DB_PORT')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop the entire public schema and recreate it
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    
    cursor.close()
    conn.close()
    print("\n" + "="*40)
    print("DATABASE WIPED SUCCESSFULLY!")
    print("="*40 + "\n")
except Exception as e:
    print(f"Error: {e}")