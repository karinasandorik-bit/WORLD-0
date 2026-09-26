import json, sqlite3, time

SCHEMA="""CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 run_id TEXT NOT NULL,
 tick INTEGER NOT NULL,
 agent_id INTEGER NOT NULL,
 arm TEXT NOT NULL,
 event_type TEXT NOT NULL,
 payload TEXT NOT NULL,
 physics_hash TEXT NOT NULL,
 created_at REAL NOT NULL
);"""

class Ledger:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute(SCHEMA)
        self.db.commit()
    def append(self,run_id,tick,agent_id,arm,event_type,payload,physics_hash):
        self.db.execute(
          "INSERT INTO events(run_id,tick,agent_id,arm,event_type,payload,physics_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
          (run_id,tick,agent_id,arm,event_type,json.dumps(payload,sort_keys=True),physics_hash,time.time()))
        self.db.commit()
    def close(self):
        self.db.close()
