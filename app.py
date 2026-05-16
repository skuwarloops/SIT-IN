from flask import Flask, request, jsonify, session, send_from_directory, redirect, send_file
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3, hashlib, os, re, atexit, json, csv, io
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

app = Flask(__name__)
app.secret_key = 'ccs-sit-in-secret-2026'
CORS(app, supports_credentials=True, origins=[
    'null', 'http://localhost', 'http://127.0.0.1',
    'http://127.0.0.1:5000', 'http://localhost:5000'
])

BASE = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(BASE, 'ccs.db')

# ══════════════════════════════════════════════════════════
#  STATIC FILE SERVING
# ══════════════════════════════════════════════════════════

@app.route('/')
def index():
    return redirect('/page/landingpage.html')

@app.route('/page/<path:filename>')
def serve_page(filename):
    return send_from_directory(os.path.join(BASE, 'page'), filename)

@app.route('/login-register/<path:filename>')
def serve_login(filename):
    return send_from_directory(os.path.join(BASE, 'login-register'), filename)

@app.route('/admin/<path:filename>')
def serve_admin(filename):
    return send_from_directory(os.path.join(BASE, 'admin'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(BASE, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(BASE, 'js'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(BASE, 'images'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(BASE, 'images'), 'favicon.ico')

# ══════════════════════════════════════════════════════════
#  DB INIT
# ══════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                id_number         TEXT    UNIQUE,
                lastname          TEXT    NOT NULL,
                firstname         TEXT    NOT NULL,
                middlename        TEXT,
                fullname          TEXT    NOT NULL,
                email             TEXT    NOT NULL UNIQUE,
                password          TEXT    NOT NULL,
                course            TEXT    NOT NULL,
                level             TEXT    NOT NULL,
                address           TEXT,
                remaining_session INTEGER NOT NULL DEFAULT 30,
                created           DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sitin (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id           INTEGER NOT NULL,
                id_number         TEXT,
                fullname          TEXT,
                purpose           TEXT,
                lab               TEXT,
                pc_number         TEXT,
                session           INTEGER,
                status            TEXT DEFAULT 'Active',
                time_in           DATETIME,
                time_out          DATETIME,
                duration_minutes  INTEGER,
                remarks           TEXT,
                is_manual         INTEGER DEFAULT 1,
                created           DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                author  TEXT NOT NULL DEFAULT 'CCS Admin',
                content TEXT NOT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER,
                type     TEXT NOT NULL,
                title    TEXT NOT NULL,
                message  TEXT NOT NULL,
                is_read  INTEGER DEFAULT 0,
                created  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                id_number  TEXT,
                fullname   TEXT,
                purpose    TEXT NOT NULL,
                lab        TEXT NOT NULL,
                date       TEXT NOT NULL,
                time_start TEXT NOT NULL,
                time_end   TEXT NOT NULL,
                status     TEXT DEFAULT 'Pending',
                created    DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                sitin_id INTEGER NOT NULL,
                user_id  INTEGER NOT NULL,
                rating   INTEGER NOT NULL,
                comment  TEXT,
                created  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sitin_id) REFERENCES sitin(id),
                FOREIGN KEY (user_id)  REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS software_apps (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT NOT NULL,
                lab_id       TEXT,
                version      TEXT,
                availability TEXT DEFAULT 'available',
                uploaded_by  INTEGER,
                created      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated      DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES admins(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id     INTEGER,
                report_type  TEXT,
                date_from    TEXT,
                date_to      TEXT,
                file_path    TEXT,
                created      DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES admins(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                recommended_time TEXT,
                recommended_lab  TEXT,
                reason       TEXT,
                confidence   REAL,
                created      DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        try:
            conn.execute(
                'INSERT INTO admins (username, password) VALUES (?,?)',
                ('admin', hashlib.sha256('admin123'.encode()).hexdigest())
            )
        except sqlite3.IntegrityError:
            pass
        conn.commit()

init_db()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def push_notification(user_id, type, title, message, conn=None):
    def _insert(c):
        c.execute(
            'INSERT INTO notifications (user_id, type, title, message) VALUES (?,?,?,?)',
            (user_id, type, title, message)
        )
    if conn:
        _insert(conn)
    else:
        with get_db() as c:
            _insert(c)
            c.commit()

def push_notification_all(type, title, message):
    with get_db() as conn:
        users = conn.execute('SELECT id FROM users').fetchall()
        for u in users:
            conn.execute(
                'INSERT INTO notifications (user_id, type, title, message) VALUES (?,?,?,?)',
                (u['id'], type, title, message)
            )
        conn.commit()

def valid_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email)

# ══════════════════════════════════════════════════════════
#  STUDENT AUTH
# ══════════════════════════════════════════════════════════

@app.route('/api/register', methods=['POST'])
def register():
    data       = request.get_json()
    id_number  = data.get('id_number',  '').strip()
    lastname   = data.get('lastname',   '').strip()
    firstname  = data.get('firstname',  '').strip()
    middlename = data.get('middlename', '').strip()
    email      = data.get('email',      '').strip().lower()
    password   = data.get('password',   '')
    confirm    = data.get('confirm',    '')
    course     = data.get('course',     '').strip()
    level      = data.get('level',      '').strip()
    address    = data.get('address',    '').strip()

    fullname = f'{lastname}, {firstname}'
    if middlename:
        fullname += f' {middlename}'

    errors = {}
    if not id_number:            errors['id_number']  = 'Student ID is required.'
    if not lastname:             errors['lastname']   = 'Last name is required.'
    if not firstname:            errors['firstname']  = 'First name is required.'
    if not email:                errors['email']      = 'Email is required.'
    elif not valid_email(email): errors['email']      = 'Enter a valid email.'
    if len(password) < 6:        errors['password']   = 'At least 6 characters required.'
    if password != confirm:      errors['confirm']    = 'Passwords do not match.'
    if not course:               errors['course']     = 'Please select a course.'
    if not level:                errors['level']      = 'Please select a year level.'
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    try:
        with get_db() as conn:
            conn.execute(
                '''INSERT INTO users
                   (id_number, lastname, firstname, middlename, fullname, email, password, course, level, address)
                   VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (id_number, lastname, firstname, middlename or None,
                 fullname, email, hash_pw(password), course, level, address or None)
            )
            conn.commit()
        return jsonify({'success': True, 'message': f'Account created for {fullname}! You can now log in.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'errors': {'email': 'Email or Student ID already registered.'}}), 400


@app.route('/api/login', methods=['POST'])
def login():
    data      = request.get_json()
    id_number = data.get('id_number', '').strip()
    password  = data.get('password',  '')

    errors = {}
    if not id_number: errors['id_number'] = 'Student ID is required.'
    if not password:  errors['password']  = 'Password is required.'
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    with get_db() as conn:
        user = conn.execute(
            'SELECT * FROM users WHERE id_number=? AND password=?',
            (id_number, hash_pw(password))
        ).fetchone()

    if not user:
        return jsonify({'success': False, 'errors': {'password': 'Incorrect ID number or password.'}}), 401

    session['user_id'] = user['id']
    return jsonify({'success': True, 'user': {
        'id':                user['id'],
        'id_number':         user['id_number'],
        'fullname':          user['fullname'],
        'lastname':          user['lastname'],
        'firstname':         user['firstname'],
        'middlename':        user['middlename'],
        'email':             user['email'],
        'course':            user['course'],
        'level':             user['level'],
        'address':           user['address'],
        'remaining_session': user['remaining_session']
    }})


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404
    return jsonify({'success': True, 'user': {
        'id':                user['id'],
        'id_number':         user['id_number'],
        'fullname':          user['fullname'],
        'lastname':          user['lastname'],
        'firstname':         user['firstname'],
        'middlename':        user['middlename'],
        'email':             user['email'],
        'course':            user['course'],
        'level':             user['level'],
        'address':           user['address'],
        'remaining_session': user['remaining_session']
    }})


# ══════════════════════════════════════════════════════════
#  ADMIN AUTH
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data     = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    with get_db() as conn:
        admin = conn.execute(
            'SELECT * FROM admins WHERE username=? AND password=?',
            (username, hash_pw(password))
        ).fetchone()
    if not admin:
        return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401
    session['admin_id']       = admin['id']
    session['admin_username'] = admin['username']
    return jsonify({'success': True, 'admin': {'id': admin['id'], 'username': admin['username']}})


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return jsonify({'success': True})


@app.route('/api/admin/me', methods=['GET'])
def admin_me():
    if not session.get('admin_id'):
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401
    return jsonify({'success': True, 'admin': {
        'id': session['admin_id'], 'username': session['admin_username']
    }})


# ══════════════════════════════════════════════════════════
#  ADMIN — STATISTICS
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        total_students  = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        currently_sitin = conn.execute("SELECT COUNT(*) FROM sitin WHERE status='Active'").fetchone()[0]
        total_sitin     = conn.execute('SELECT COUNT(*) FROM sitin').fetchone()[0]
        purpose_counts  = conn.execute(
            "SELECT purpose, COUNT(*) as cnt FROM sitin GROUP BY purpose ORDER BY cnt DESC"
        ).fetchall()
    return jsonify({'success': True, 'stats': {
        'total_students':  total_students,
        'currently_sitin': currently_sitin,
        'total_sitin':     total_sitin,
        'purpose_counts':  [dict(r) for r in purpose_counts]
    }})


# ══════════════════════════════════════════════════════════
#  ADMIN — STUDENTS
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/students', methods=['GET'])
def get_students():
    with get_db() as conn:
        rows = conn.execute(
            'SELECT id, id_number, lastname, firstname, middlename, fullname, email, course, level, address, remaining_session FROM users ORDER BY lastname, firstname'
        ).fetchall()
    return jsonify({'success': True, 'students': [dict(r) for r in rows]})


@app.route('/api/admin/students', methods=['POST'])
def add_student():
    data       = request.get_json()
    lastname   = data.get('lastname',   '').strip()
    firstname  = data.get('firstname',  '').strip()
    middlename = data.get('middlename', '').strip()
    email      = data.get('email',      '').strip().lower()
    id_number  = data.get('id_number',  '').strip()
    course     = data.get('course',     '').strip()
    level      = data.get('level',      '').strip()
    sessions   = int(data.get('remaining_session', 30))
    fullname   = f'{lastname}, {firstname}'
    if middlename:
        fullname += f' {middlename}'
    if not firstname or not lastname or not email:
        return jsonify({'success': False, 'message': 'Name and email required.'}), 400
    try:
        with get_db() as conn:
            conn.execute(
                '''INSERT INTO users (id_number, lastname, firstname, middlename, fullname, email, password, course, level, remaining_session)
                   VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (id_number or None, lastname, firstname, middlename or None,
                 fullname, email, hash_pw('password123'), course, level, sessions)
            )
            conn.commit()
        return jsonify({'success': True, 'message': 'Student added.'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email or ID already exists.'}), 400


@app.route('/api/admin/students/<int:sid>', methods=['PUT'])
def edit_student(sid):
    data       = request.get_json()
    lastname   = data.get('lastname',   '').strip()
    firstname  = data.get('firstname',  '').strip()
    middlename = data.get('middlename', '').strip()
    fullname   = f'{lastname}, {firstname}'
    if middlename:
        fullname += f' {middlename}'
    with get_db() as conn:
        conn.execute(
            '''UPDATE users SET id_number=?, lastname=?, firstname=?, middlename=?, fullname=?,
               email=?, course=?, level=?, remaining_session=? WHERE id=?''',
            (data.get('id_number'), lastname, firstname, middlename or None, fullname,
             data.get('email'), data.get('course'), data.get('level'),
             int(data.get('remaining_session', 30)), sid)
        )
        conn.commit()
    return jsonify({'success': True, 'message': 'Student updated.'})


@app.route('/api/admin/students/<int:sid>', methods=['DELETE'])
def delete_student(sid):
    with get_db() as conn:
        conn.execute('DELETE FROM users WHERE id=?', (sid,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Student deleted.'})


@app.route('/api/admin/students/search', methods=['GET'])
def search_students():
    q = request.args.get('q', '').strip()
    with get_db() as conn:
        rows = conn.execute(
            '''SELECT id, id_number, lastname, firstname, middlename, fullname, email, course, level, remaining_session
               FROM users WHERE fullname LIKE ? OR id_number LIKE ? OR email LIKE ?
               OR lastname LIKE ? OR firstname LIKE ?
               ORDER BY lastname, firstname''',
            (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%')
        ).fetchall()
    return jsonify({'success': True, 'students': [dict(r) for r in rows]})


@app.route('/api/admin/students/reset-sessions', methods=['POST'])
def reset_all_sessions():
    with get_db() as conn:
        conn.execute('UPDATE users SET remaining_session = 30')
        conn.commit()
    return jsonify({'success': True, 'message': 'All sessions reset to 30.'})


# ══════════════════════════════════════════════════════════
#  ADMIN — SIT-IN
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/sitin', methods=['GET'])
def get_sitin():
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM sitin ORDER BY created DESC').fetchall()
    return jsonify({'success': True, 'records': [dict(r) for r in rows]})


@app.route('/api/admin/sitin', methods=['POST'])
def create_sitin():
    data      = request.get_json()
    id_number = data.get('id_number', '').strip()
    purpose   = data.get('purpose',   '').strip()
    lab       = data.get('lab',       '').strip()

    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id_number=?', (id_number,)).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Student ID not found.'}), 404
        if user['remaining_session'] <= 0:
            return jsonify({'success': False, 'message': 'No remaining sessions.'}), 400
        active = conn.execute(
            "SELECT id FROM sitin WHERE user_id=? AND status='Active'", (user['id'],)
        ).fetchone()
        if active:
            return jsonify({'success': False, 'message': 'Student already has an active sit-in.'}), 400
        conn.execute(
            'INSERT INTO sitin (user_id, id_number, fullname, purpose, lab, session, status) VALUES (?,?,?,?,?,?,?)',
            (user['id'], id_number, user['fullname'], purpose, lab, user['remaining_session'], 'Active')
        )
        conn.execute('UPDATE users SET remaining_session = remaining_session - 1 WHERE id=?', (user['id'],))
        conn.commit()
        updated = conn.execute('SELECT remaining_session FROM users WHERE id=?', (user['id'],)).fetchone()

    return jsonify({'success': True,
                    'message': f'Sit-in started for {user["fullname"]}.',
                    'student': {'fullname': user['fullname'],
                                'remaining_session': updated['remaining_session']}})


@app.route('/api/admin/sitin/<int:sit_id>/end', methods=['POST'])
def end_sitin(sit_id):
    with get_db() as conn:
        sit = conn.execute('SELECT * FROM sitin WHERE id=?', (sit_id,)).fetchone()
        conn.execute("UPDATE sitin SET status='Done' WHERE id=?", (sit_id,))
        conn.commit()
    if sit:
        push_notification(sit['user_id'], 'sitin',
            '🏁 Sit-in Session Ended',
            f'Your sit-in session for {sit["purpose"]} in {sit["lab"]} has been ended.')
    return jsonify({'success': True, 'message': 'Sit-in ended.'})


@app.route('/api/admin/sitin/<int:sit_id>', methods=['DELETE'])
def delete_sitin(sit_id):
    with get_db() as conn:
        conn.execute('DELETE FROM sitin WHERE id=?', (sit_id,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Record deleted.'})


# ══════════════════════════════════════════════════════════
#  ADMIN — ANNOUNCEMENTS
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/announcements', methods=['GET'])
def get_announcements():
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM announcements ORDER BY created DESC').fetchall()
    return jsonify({'success': True, 'announcements': [dict(r) for r in rows]})


@app.route('/api/admin/announcements', methods=['POST'])
def post_announcement():
    data    = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'message': 'Content required.'}), 400
    with get_db() as conn:
        conn.execute('INSERT INTO announcements (content) VALUES (?)', (content,))
        conn.commit()
    push_notification_all(
        'announcement',
        '📢 New Announcement',
        content[:120] + ('...' if len(content) > 120 else '')
    )
    return jsonify({'success': True, 'message': 'Announcement posted.'})


@app.route('/api/admin/announcements/<int:aid>', methods=['DELETE'])
def delete_announcement(aid):
    with get_db() as conn:
        ann = conn.execute('SELECT * FROM announcements WHERE id=?', (aid,)).fetchone()
        if ann:
            msg = ann['content'][:120] + ('...' if len(ann['content']) > 120 else '')
            conn.execute('DELETE FROM notifications WHERE type=? AND message=?', ('announcement', msg))
        conn.execute('DELETE FROM announcements WHERE id=?', (aid,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Deleted.'})


# ══════════════════════════════════════════════════════════
#  STUDENT — NOTIFICATIONS
# ══════════════════════════════════════════════════════════

@app.route('/api/notifications/<int:uid>', methods=['GET'])
def get_notifications(uid):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM notifications WHERE user_id=? ORDER BY created DESC LIMIT 20', (uid,)
        ).fetchall()
    return jsonify({'success': True, 'notifications': [dict(r) for r in rows]})


@app.route('/api/notifications/<int:uid>/unread-count', methods=['GET'])
def get_unread_count(uid):
    with get_db() as conn:
        count = conn.execute(
            'SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0', (uid,)
        ).fetchone()[0]
    return jsonify({'success': True, 'count': count})


@app.route('/api/notifications/<int:uid>/mark-read', methods=['POST'])
def mark_all_read(uid):
    with get_db() as conn:
        conn.execute('UPDATE notifications SET is_read=1 WHERE user_id=?', (uid,))
        conn.commit()
    return jsonify({'success': True})


@app.route('/api/notifications/<int:nid>/read', methods=['POST'])
def mark_one_read(nid):
    with get_db() as conn:
        conn.execute('UPDATE notifications SET is_read=1 WHERE id=?', (nid,))
        conn.commit()
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════
#  STUDENT — EDIT PROFILE
# ══════════════════════════════════════════════════════════

@app.route('/api/profile/<int:uid>', methods=['PUT'])
def update_profile(uid):
    data       = request.get_json()
    lastname   = data.get('lastname',   '').strip()
    firstname  = data.get('firstname',  '').strip()
    middlename = data.get('middlename', '').strip()
    email      = data.get('email',      '').strip().lower()
    address    = data.get('address',    '').strip()

    if not lastname or not firstname or not email:
        return jsonify({'success': False, 'message': 'Name and email are required.'}), 400

    fullname = f'{lastname}, {firstname}'
    if middlename:
        fullname += f' {middlename}'

    try:
        with get_db() as conn:
            conn.execute(
                '''UPDATE users SET lastname=?, firstname=?, middlename=?, fullname=?,
                   email=?, address=? WHERE id=?''',
                (lastname, firstname, middlename or None, fullname, email, address or None, uid)
            )
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
        return jsonify({'success': True, 'message': 'Profile updated successfully!', 'user': {
            'id': user['id'], 'id_number': user['id_number'],
            'fullname': user['fullname'], 'lastname': user['lastname'],
            'firstname': user['firstname'], 'middlename': user['middlename'],
            'email': user['email'], 'course': user['course'],
            'level': user['level'], 'address': user['address'],
            'remaining_session': user['remaining_session']
        }})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ══════════════════════════════════════════════════════════
#  STUDENT — SIT-IN HISTORY
# ══════════════════════════════════════════════════════════

@app.route('/api/history/<int:uid>', methods=['GET'])
def get_student_history(uid):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM sitin WHERE user_id=? ORDER BY created DESC', (uid,)
        ).fetchall()
        history = []
        for r in rows:
            d  = dict(r)
            fb = conn.execute(
                'SELECT id FROM feedback WHERE sitin_id=? AND user_id=?', (r['id'], uid)
            ).fetchone()
            d['feedback_submitted'] = bool(fb)
            history.append(d)
    return jsonify({'success': True, 'history': history})


# ══════════════════════════════════════════════════════════
#  STUDENT — FEEDBACK
# ══════════════════════════════════════════════════════════

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data     = request.get_json()
    sitin_id = data.get('sitin_id')
    user_id  = data.get('user_id')
    rating   = data.get('rating')
    comment  = data.get('comment', '').strip()

    if not all([sitin_id, user_id, rating]):
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400
    if not (1 <= int(rating) <= 5):
        return jsonify({'success': False, 'message': 'Rating must be 1-5.'}), 400

    with get_db() as conn:
        existing = conn.execute(
            'SELECT id FROM feedback WHERE sitin_id=? AND user_id=?', (sitin_id, user_id)
        ).fetchone()
        if existing:
            return jsonify({'success': False, 'message': 'Feedback already submitted.'}), 400
        conn.execute(
            'INSERT INTO feedback (sitin_id, user_id, rating, comment) VALUES (?,?,?,?)',
            (sitin_id, user_id, rating, comment or None)
        )
        conn.commit()

    return jsonify({'success': True, 'message': 'Feedback submitted!'})


@app.route('/api/admin/feedback', methods=['GET'])
def get_all_feedback():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT f.id, f.rating, f.comment, f.created,
                   u.fullname, u.id_number,
                   s.purpose, s.lab
            FROM feedback f
            JOIN users u ON f.user_id  = u.id
            JOIN sitin s ON f.sitin_id = s.id
            ORDER BY f.created DESC
        ''').fetchall()
    return jsonify({'success': True, 'feedback': [dict(r) for r in rows]})


# ══════════════════════════════════════════════════════════
#  STUDENT — RESERVATIONS
# ══════════════════════════════════════════════════════════

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data    = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Not authenticated.'}), 401

    purpose    = data.get('purpose',    '').strip()
    lab        = data.get('lab',        '').strip()
    date       = data.get('date',       '').strip()
    time_start = data.get('time_start', '').strip()
    time_end   = data.get('time_end',   '').strip()

    if not all([purpose, lab, date, time_start, time_end]):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'Student not found.'}), 404
        conn.execute(
            '''INSERT INTO reservations (user_id, id_number, fullname, purpose, lab, date, time_start, time_end, status)
               VALUES (?,?,?,?,?,?,?,?,?)''',
            (user_id, user['id_number'], user['fullname'], purpose, lab, date, time_start, time_end, 'Pending')
        )
        conn.commit()
    return jsonify({'success': True, 'message': 'Reservation submitted successfully!'})


@app.route('/api/reservations/<int:uid>', methods=['GET'])
def get_my_reservations(uid):
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM reservations WHERE user_id=? ORDER BY created DESC', (uid,)
        ).fetchall()
    return jsonify({'success': True, 'reservations': [dict(r) for r in rows]})


@app.route('/api/reservations/<int:rid>/cancel', methods=['POST'])
def cancel_reservation(rid):
    with get_db() as conn:
        res = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
        if not res:
            return jsonify({'success': False, 'message': 'Reservation not found.'}), 404
        if res['status'] != 'Pending':
            return jsonify({'success': False, 'message': 'Only pending reservations can be cancelled.'}), 400
        conn.execute("UPDATE reservations SET status='Cancelled' WHERE id=?", (rid,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Reservation cancelled.'})


# ══════════════════════════════════════════════════════════
#  ADMIN — RESERVATIONS
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/reservations', methods=['GET'])
def get_all_reservations():
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM reservations ORDER BY date ASC, time_start ASC'
        ).fetchall()
    return jsonify({'success': True, 'reservations': [dict(r) for r in rows]})


@app.route('/api/admin/reservations/<int:rid>/approve', methods=['POST'])
def approve_reservation(rid):
    from datetime import datetime

    with get_db() as conn:
        conn.execute("UPDATE reservations SET status='Approved' WHERE id=?", (rid,))
        conn.commit()

        res = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
        if not res:
            return jsonify({'success': False, 'message': 'Reservation not found.'}), 404

        now       = datetime.now()
        today_str = now.strftime('%Y-%m-%d')
        now_time  = now.strftime('%H:%M')

        sitin_created = False
        if res['date'] == today_str and res['time_start'] <= now_time <= res['time_end']:
            active = conn.execute(
                "SELECT id FROM sitin WHERE user_id=? AND status='Active'", (res['user_id'],)
            ).fetchone()
            user = conn.execute('SELECT * FROM users WHERE id=?', (res['user_id'],)).fetchone()
            if not active and user and user['remaining_session'] > 0:
                conn.execute(
                    '''INSERT INTO sitin (user_id, id_number, fullname, purpose, lab, session, status)
                       VALUES (?,?,?,?,?,?,?)''',
                    (res['user_id'], res['id_number'], res['fullname'],
                     res['purpose'], res['lab'], user['remaining_session'], 'Active')
                )
                conn.execute(
                    'UPDATE users SET remaining_session = remaining_session - 1 WHERE id=?',
                    (res['user_id'],)
                )
                conn.commit()
                sitin_created = True

    msg = 'Reservation approved.'
    if sitin_created:
        msg = 'Reservation approved and sit-in session started automatically.'
        push_notification(res['user_id'], 'sitin',
            '✅ Sit-in Started',
            f'Your reservation for {res["purpose"]} in {res["lab"]} has been approved and your sit-in session has started.')
    else:
        push_notification(res['user_id'], 'reservation',
            '✅ Reservation Approved',
            f'Your reservation for {res["purpose"]} in {res["lab"]} on {res["date"]} has been approved.')
    return jsonify({'success': True, 'message': msg, 'sitin_created': sitin_created})


@app.route('/api/admin/reservations/<int:rid>/reject', methods=['POST'])
def reject_reservation(rid):
    with get_db() as conn:
        res = conn.execute('SELECT * FROM reservations WHERE id=?', (rid,)).fetchone()
        conn.execute("UPDATE reservations SET status='Rejected' WHERE id=?", (rid,))
        conn.commit()
    if res:
        push_notification(res['user_id'], 'reservation',
            '❌ Reservation Rejected',
            f'Your reservation for {res["purpose"]} in {res["lab"]} on {res["date"]} has been rejected.')
    return jsonify({'success': True, 'message': 'Reservation rejected.'})


@app.route('/api/admin/reservations/<int:rid>', methods=['DELETE'])
def delete_reservation(rid):
    with get_db() as conn:
        conn.execute('DELETE FROM reservations WHERE id=?', (rid,))
        conn.commit()
    return jsonify({'success': True, 'message': 'Reservation deleted.'})




# ══════════════════════════════════════════════════════════
#  STUDENT FEATURES - SIT-IN SUMMARY & HISTORY
# ══════════════════════════════════════════════════════════

@app.route('/api/student/sit-in-summary', methods=['GET'])
def get_sitin_summary():
    """Returns user's sit-in statistics"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    
    # Get all sessions for this user
    sessions = conn.execute(
        '''SELECT * FROM sitin WHERE user_id=? AND status IN ('Active', 'Done')
           ORDER BY created DESC''',
        (user['id'],)
    ).fetchall()
    
    total_sessions = len(sessions)
    durations = []
    
    for s in sessions:
        if s['duration_minutes']:
            durations.append(s['duration_minutes'])
    
    avg_duration = round(statistics.mean(durations)) if durations else 0
    longest_session = max(durations) if durations else 0
    
    sessions_data = []
    for s in sessions:
        sessions_data.append({
            'id': s['id'],
            'date': s['created'][:10] if s['created'] else '',
            'time_in': s['time_in'],
            'time_out': s['time_out'],
            'duration_minutes': s['duration_minutes'],
            'pc_number': s['pc_number'],
            'lab': s['lab'],
            'purpose': s['purpose'],
            'status': s['status'],
            'remarks': s['remarks']
        })
    
    conn.close()
    
    return jsonify({
        'summary': {
            'total_sessions': total_sessions,
            'avg_duration_minutes': avg_duration,
            'longest_session_minutes': longest_session
        },
        'sessions': sessions_data
    })


@app.route('/api/student/sitin/start', methods=['POST'])
def start_sitin():
    """Start a sit-in session - manual or auto"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json() or {}
    lab = data.get('lab')
    pc_number = data.get('pc_number', '')
    purpose = data.get('purpose', '')
    is_manual = data.get('is_manual', True)
    
    if not lab:
        return jsonify({'error': 'Lab is required'}), 400
    
    conn = get_db()
    time_in = datetime.now().isoformat()
    
    conn.execute('''
        INSERT INTO sitin (user_id, id_number, fullname, lab, purpose, pc_number, 
                          status, time_in, is_manual)
        VALUES (?, ?, ?, ?, ?, ?, 'Active', ?, ?)
    ''', (user['id'], user['id_number'], user['fullname'], lab, purpose, pc_number, time_in, 1 if is_manual else 0))
    
    sitin_id = conn.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'sitin_id': sitin_id, 'time_in': time_in})


@app.route('/api/student/sitin/<int:sid>/end', methods=['POST'])
def end_sitin_session(sid):
    """End a sit-in session"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json() or {}
    remarks = data.get('remarks', '')
    
    conn = get_db()
    sitin = conn.execute('SELECT * FROM sitin WHERE id=? AND user_id=?', (sid, user['id'])).fetchone()
    
    if not sitin:
        conn.close()
        return jsonify({'error': 'Sit-in not found'}), 404
    
    time_out = datetime.now().isoformat()
    time_in = datetime.fromisoformat(sitin['time_in'])
    duration = int((datetime.now() - time_in).total_seconds() / 60)
    
    conn.execute('''
        UPDATE sitin SET status='Done', time_out=?, duration_minutes=?, remarks=?
        WHERE id=?
    ''', (time_out, duration, remarks, sid))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'time_out': time_out,
        'duration_minutes': duration
    })


@app.route('/api/student/history', methods=['GET'])
def get_history():
    """Get detailed sit-in history for student"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    sessions = conn.execute(
        '''SELECT * FROM sitin WHERE user_id=? ORDER BY created DESC''',
        (user['id'],)
    ).fetchall()
    
    sessions_data = []
    for s in sessions:
        sessions_data.append({
            'id': s['id'],
            'date': s['created'][:10],
            'time_in': s['time_in'],
            'time_out': s['time_out'],
            'duration_minutes': s['duration_minutes'],
            'pc_number': s['pc_number'],
            'lab': s['lab'],
            'purpose': s['purpose'],
            'status': s['status'],
            'remarks': s['remarks'],
            'is_manual': bool(s['is_manual'])
        })
    
    conn.close()
    return jsonify(sessions_data)


# ══════════════════════════════════════════════════════════
#  SOFTWARE AVAILABILITY
# ══════════════════════════════════════════════════════════

@app.route('/api/software/available', methods=['GET'])
def get_available_software():
    """Get available software per lab"""
    lab = request.args.get('lab')
    
    conn = get_db()
    
    if lab:
        software = conn.execute(
            'SELECT * FROM software_apps WHERE (lab_id=? OR lab_id IS NULL) AND availability="available"',
            (lab,)
        ).fetchall()
    else:
        software = conn.execute(
            'SELECT * FROM software_apps WHERE availability="available" ORDER BY lab_id'
        ).fetchall()
    
    result = {}
    for s in software:
        lab_name = s['lab_id'] or 'General'
        if lab_name not in result:
            result[lab_name] = []
        result[lab_name].append({
            'id': s['id'],
            'name': s['name'],
            'version': s['version']
        })
    
    conn.close()
    return jsonify(result)


@app.route('/api/admin/software', methods=['GET'])
def get_all_software():
    """Get all software (admin)"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    conn = get_db()
    software = conn.execute('SELECT * FROM software_apps ORDER BY lab_id, name').fetchall()
    
    result = []
    for s in software:
        result.append({
            'id': s['id'],
            'name': s['name'],
            'lab_id': s['lab_id'],
            'version': s['version'],
            'availability': s['availability'],
            'created': s['created']
        })
    
    conn.close()
    return jsonify(result)


@app.route('/api/admin/software', methods=['POST'])
def add_software():
    """Add new software (admin)"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    data = request.get_json() or {}
    name = data.get('name')
    lab_id = data.get('lab_id')
    version = data.get('version', '')
    
    if not name:
        return jsonify({'error': 'Name required'}), 400
    
    conn = get_db()
    conn.execute(
        'INSERT INTO software_apps (name, lab_id, version, uploaded_by) VALUES (?, ?, ?, ?)',
        (name, lab_id, version, admin['id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/api/admin/software/<int:sid>', methods=['PUT'])
def update_software(sid):
    """Update software (admin)"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    data = request.get_json() or {}
    availability = data.get('availability')
    
    if not availability:
        return jsonify({'error': 'Availability required'}), 400
    
    conn = get_db()
    conn.execute(
        'UPDATE software_apps SET availability=?, updated=? WHERE id=?',
        (availability, datetime.now().isoformat(), sid)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/api/admin/software/<int:sid>', methods=['DELETE'])
def delete_software(sid):
    """Delete software (admin)"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    conn = get_db()
    conn.execute('DELETE FROM software_apps WHERE id=?', (sid,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════
#  ANALYTICS & REPORTS
# ══════════════════════════════════════════════════════════

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data: usage patterns, peak hours, etc."""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    days = request.args.get('days', 30, type=int)
    date_from = (datetime.now() - timedelta(days=days)).date()
    
    conn = get_db()
    
    # Total sessions
    total_sessions = conn.execute(
        'SELECT COUNT(*) as cnt FROM sitin WHERE created >= ?',
        (str(date_from),)
    ).fetchone()['cnt']
    
    # Peak hours analysis
    sessions = conn.execute(
        '''SELECT strftime('%H', time_in) as hour, COUNT(*) as cnt 
           FROM sitin WHERE time_in IS NOT NULL AND created >= ?
           GROUP BY hour ORDER BY cnt DESC''',
        (str(date_from),)
    ).fetchall()
    
    peak_hours = []
    for s in sessions:
        if s['hour']:
            peak_hours.append({'hour': s['hour'], 'count': s['cnt']})
    
    # Peak days analysis
    days_data = conn.execute(
        '''SELECT strftime('%w', created) as day_num, COUNT(*) as cnt 
           FROM sitin WHERE created >= ?
           GROUP BY day_num ORDER BY cnt DESC''',
        (str(date_from),)
    ).fetchall()
    
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    peak_days = []
    for d in days_data:
        day_name = day_names[int(d['day_num'])]
        peak_days.append({'day': day_name, 'count': d['cnt']})
    
    # Lab utilization
    labs = conn.execute(
        '''SELECT lab, COUNT(*) as cnt FROM sitin WHERE created >= ?
           GROUP BY lab ORDER BY cnt DESC''',
        (str(date_from),)
    ).fetchall()
    
    lab_util = []
    for l in labs:
        lab_util.append({'lab': l['lab'], 'sessions': l['cnt']})
    
    # Average session duration
    durations = conn.execute(
        'SELECT duration_minutes FROM sitin WHERE duration_minutes > 0 AND created >= ?',
        (str(date_from),)
    ).fetchall()
    
    avg_duration = round(statistics.mean([d['duration_minutes'] for d in durations])) if durations else 0
    
    # Unique students
    unique_students = conn.execute(
        'SELECT COUNT(DISTINCT user_id) as cnt FROM sitin WHERE created >= ?',
        (str(date_from),)
    ).fetchone()['cnt']
    
    conn.close()
    
    return jsonify({
        'date_range': days,
        'total_sessions': total_sessions,
        'unique_students': unique_students,
        'avg_duration_minutes': avg_duration,
        'peak_hours': peak_hours[:5],
        'peak_days': peak_days,
        'lab_utilization': lab_util
    })


@app.route('/api/admin/reports/generate', methods=['POST'])
def generate_report():
    """Generate comprehensive PDF/CSV report"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    data = request.get_json() or {}
    report_format = data.get('format', 'csv')  # csv or pdf
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    lab_filter = data.get('lab')
    
    conn = get_db()
    
    # Build query
    query = 'SELECT * FROM sitin WHERE 1=1'
    params = []
    
    if date_from:
        query += ' AND created >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND created <= ?'
        params.append(date_to)
    if lab_filter:
        query += ' AND lab = ?'
        params.append(lab_filter)
    
    query += ' ORDER BY created DESC'
    sessions = conn.execute(query, params).fetchall()
    
    if report_format == 'csv':
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = ['ID', 'Student Name', 'ID Number', 'Lab', 'PC Number', 'Purpose', 
                  'Time In', 'Time Out', 'Duration (min)', 'Status', 'Date', 'Remarks']
        writer.writerow(headers)
        
        # Data
        for s in sessions:
            writer.writerow([
                s['id'],
                s['fullname'],
                s['id_number'],
                s['lab'],
                s['pc_number'],
                s['purpose'],
                s['time_in'],
                s['time_out'],
                s['duration_minutes'],
                s['status'],
                s['created'][:10],
                s['remarks']
            ])
        
        output.seek(0)
        filename = f"sit-in-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        
        # Save to database
        conn.execute(
            'INSERT INTO reports (admin_id, report_type, date_from, date_to, file_path) VALUES (?, ?, ?, ?, ?)',
            (admin['id'], 'csv', date_from, date_to, filename)
        )
        conn.commit()
        conn.close()
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    conn.close()
    return jsonify({'error': 'PDF format not yet implemented'}), 501


@app.route('/api/admin/reports/list', methods=['GET'])
def list_reports():
    """List all generated reports"""
    admin = session.get('admin')
    if not admin:
        return jsonify({'error': 'Not admin'}), 401
    
    conn = get_db()
    reports = conn.execute(
        'SELECT * FROM reports ORDER BY created DESC'
    ).fetchall()
    
    result = []
    for r in reports:
        result.append({
            'id': r['id'],
            'type': r['report_type'],
            'date_range': f"{r['date_from']} to {r['date_to']}",
            'created': r['created']
        })
    
    conn.close()
    return jsonify(result)


# ══════════════════════════════════════════════════════════
#  AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════

@app.route('/api/student/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-powered sit-in recommendations for student"""
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    
    # Get user's sit-in history
    sessions = conn.execute(
        '''SELECT strftime('%H', time_in) as hour, lab, COUNT(*) as cnt 
           FROM sitin WHERE user_id=? AND time_in IS NOT NULL
           GROUP BY hour, lab ORDER BY cnt DESC LIMIT 5''',
        (user['id'],)
    ).fetchall()
    
    recommendations = []
    
    if sessions:
        # Find most frequent hour and lab
        hour_freq = defaultdict(int)
        lab_freq = defaultdict(int)
        
        for s in sessions:
            if s['hour']:
                hour_freq[s['hour']] += s['cnt']
            if s['lab']:
                lab_freq[s['lab']] += s['cnt']
        
        best_hour = max(hour_freq, key=hour_freq.get) if hour_freq else '14'
        best_lab = max(lab_freq, key=lab_freq.get) if lab_freq else 'Lab 1'
        
        recommendations.append({
            'type': 'optimal_time',
            'time': f"{best_hour}:00",
            'lab': best_lab,
            'reason': 'Based on your sit-in history, this is your most productive time',
            'confidence': 0.85
        })
        
        # Recommend less crowded time
        crowded_hour = int(best_hour)
        quiet_hour = (crowded_hour + 2) % 24
        recommendations.append({
            'type': 'quiet_time',
            'time': f"{quiet_hour:02d}:00",
            'lab': best_lab,
            'reason': 'This time is typically less crowded',
            'confidence': 0.75
        })
        
        # Save to database
        for rec in recommendations:
            conn.execute(
                '''INSERT INTO ai_recommendations (user_id, recommended_time, recommended_lab, reason, confidence)
                   VALUES (?, ?, ?, ?, ?)''',
                (user['id'], rec['time'], rec['lab'], rec['reason'], rec['confidence'])
            )
    
    conn.commit()
    conn.close()
    
    return jsonify(recommendations if recommendations else [
        {
            'type': 'no_history',
            'message': 'Start your first sit-in to receive personalized recommendations!',
            'confidence': 0
        }
    ])


# ══════════════════════════════════════════════════════════
#  BACKGROUND SCHEDULER — AUTO-END SIT-INS
# ══════════════════════════════════════════════════════════


def auto_end_sitins():
    from datetime import datetime
    now       = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    now_time  = now.strftime('%H:%M')

    with get_db() as conn:
        active_sitins = conn.execute(
            "SELECT s.id, s.user_id FROM sitin s WHERE s.status='Active'"
        ).fetchall()
        for sitin in active_sitins:
            res = conn.execute(
                """SELECT r.time_end FROM reservations r
                   WHERE r.user_id=? AND r.date=? AND r.status='Approved'
                   AND r.time_end <= ?""",
                (sitin['user_id'], today_str, now_time)
            ).fetchone()
            if res:
                conn.execute("UPDATE sitin SET status='Done' WHERE id=?", (sitin['id'],))
        conn.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(func=auto_end_sitins, trigger='interval', minutes=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    print("CCS Backend running — open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000, use_reloader=False)