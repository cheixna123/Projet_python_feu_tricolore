import sqlite3

class Database:
    def __init__(self, db_name="traffic.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_log_table()

    def create_log_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                type_action TEXT,
                action TEXT,
                etat_feu TEXT,
                scenario TEXT
            )
        ''')
        self.conn.commit()

    def insert_log(self, timestamp, type_action, action, etat_feu, scenario):
        self.cursor.execute('''
            INSERT INTO log (timestamp, type_action, action, etat_feu, scenario)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, type_action, action, etat_feu, scenario))
        self.conn.commit()
