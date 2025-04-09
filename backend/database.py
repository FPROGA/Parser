import psycopg2
from psycopg2.extras import execute_values
import json
# подключение к PostgreSQL
class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="parser",
                user="postgres",
                password="TemaiSofaBF1!",
                host="localhost",
                port="5433",
                options="-c client_encoding=utf8"
            )
            print("✅ Успешное подключение к PostgreSQL!")
            self._create_table_if_not_exists()
        except Exception as e:
            print(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise

    def _create_table_if_not_exists(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                 CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                hard_skills JSONB,  
                soft_skills TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()
    
    def insert_candidate(self, data):
        with self.conn.cursor() as cur:
            hard_skills_json = json.dumps(data["hard_skills"])
            soft_skills_array = data["soft_skills"]  
            print("hard_skills_json")
            cur.execute("""
            INSERT INTO candidates (first_name, last_name, hard_skills, soft_skills)
            VALUES (%s, %s, %s::jsonb, %s::text[])
            """, (
            data["first_name"],
            data["last_name"],
            hard_skills_json,
            soft_skills_array
        ))
        self.conn.commit()