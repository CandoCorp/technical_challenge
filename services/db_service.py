import sqlite3
from typing import List, Generator
from models import School
from config import settings

class DBService:
    def __init__(self):
        self.db_path = settings.DB_FILE
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schools (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def insert_schools(self, schools: List[School]):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Batch insert
        data = [(s.id, s.name, s.city, s.state) for s in schools]
        cursor.executemany("""
            INSERT OR REPLACE INTO schools (id, name, city, state)
            VALUES (?, ?, ?, ?)
        """, data)
        
        conn.commit()
        conn.close()

    def get_all_schools(self) -> Generator[School, None, None]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, city, state FROM schools")
        
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                yield School(
                    NCESSCH=row['id'],
                    SCHNAM05=row['name'],
                    LCITY05=row['city'],
                    LSTATE05=row['state']
                )
        conn.close()

    def clear_data(self):
        conn = self.get_connection()
        conn.execute("DELETE FROM schools")
        conn.commit()
        conn.close()

db_service = DBService()
