import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccs.db')
conn = sqlite3.connect(DB)
conn.execute('DROP TABLE IF EXISTS notifications')
conn.execute('''CREATE TABLE notifications (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER,
    type     TEXT NOT NULL,
    title    TEXT NOT NULL,
    message  TEXT NOT NULL,
    is_read  INTEGER DEFAULT 0,
    created  DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()
conn.close()
print('Done!')