import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccs.db')
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# Only get the latest announcement
latest = conn.execute('SELECT * FROM announcements ORDER BY created DESC LIMIT 1').fetchone()
users = conn.execute('SELECT id FROM users').fetchall()

if latest:
    msg = latest['content'][:120] + ('...' if len(latest['content']) > 120 else '')
    for u in users:
        conn.execute(
            'INSERT INTO notifications (user_id, type, title, message) VALUES (?,?,?,?)',
            (u['id'], 'announcement', '📢 New Announcement', msg)
        )
    conn.commit()
    print(f'Notified all users about: {msg}')
else:
    print('No announcements found.')

conn.close()