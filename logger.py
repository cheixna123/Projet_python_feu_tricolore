from datetime import datetime

class Logger:
    def __init__(self, database):
        self.db = database

    def log_action(self, type_action, action, etat_feu, scenario):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.insert_log(timestamp, type_action, action, etat_feu, scenario)
