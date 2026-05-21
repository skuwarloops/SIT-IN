"""
Run this script once to seed all lab software into your ccs.db.
Place this file next to your ccs.db and run:
    python seed_software.py
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccs.db')

software_list = [
    # ── General (shows in ALL labs) ──────────────────────
    ('Google Chrome',       'v124',      None),
    ('Microsoft Edge',      'v124',      None),
    ('7-Zip',               'v24.05',    None),
    ('Zoom',                'v5.17',     None),
    ('LibreOffice',         'v24.2',     None),

    # ── Lab 524 — Programming ────────────────────────────
    ('XAMPP',               'v8.2.4',    'Lab 524'),
    ('NetBeans',            'v19.0',     'Lab 524'),
    ('Eclipse',             '2024-03',   'Lab 524'),
    ('MySQL Workbench',     'v8.0.36',   'Lab 524'),
    ('Cisco Packet Tracer', 'v8.2',      'Lab 524'),

    # ── Lab 526 — Web & Scripting ────────────────────────
    ('Visual Studio Code',  'v1.89',     'Lab 526'),
    ('Python',              'v3.12',     'Lab 526'),
    ('Git',                 'v2.44',     'Lab 526'),
    ('Postman',             'v10.24',    'Lab 526'),
    ('Node.js',             'v20.12',    'Lab 526'),

    # ── Lab 528 — Mobile & Java ──────────────────────────
    ('Android Studio',      'Iguana',    'Lab 528'),
    ('Java JDK',            'v21 LTS',   'Lab 528'),
    ('NetBeans',            'v19.0',     'Lab 528'),
    ('MySQL Workbench',     'v8.0.36',   'Lab 528'),
    ('Figma Desktop',       'v116',      'Lab 528'),

    # ── Lab 530 — Multimedia & Game Dev ─────────────────
    ('Unity',               '2023 LTS',  'Lab 530'),
    ('Blender',             'v4.1',      'Lab 530'),
    ('Adobe Photoshop',     'CC 2024',   'Lab 530'),
    ('Visual Studio Code',  'v1.89',     'Lab 530'),
    ('OBS Studio',          'v30.1',     'Lab 530'),

    # ── Lab 540 — Networking & General ──────────────────
    ('Cisco Packet Tracer', 'v8.2',      'Lab 540'),
    ('Wireshark',           'v4.2',      'Lab 540'),
    ('PuTTY',               'v0.81',     'Lab 540'),
    ('VirtualBox',          'v7.0',      'Lab 540'),
    ('XAMPP',               'v8.2.4',    'Lab 540'),
]

def seed():
    conn = sqlite3.connect(DB)
    inserted = 0
    skipped  = 0

    for name, version, lab_id in software_list:
        # Skip if already exists for same name + lab
        existing = conn.execute(
            'SELECT id FROM software_apps WHERE name=? AND (lab_id=? OR (lab_id IS NULL AND ? IS NULL))',
            (name, lab_id, lab_id)
        ).fetchone()

        if existing:
            print(f'  SKIP  {name} ({lab_id or "General"}) — already exists')
            skipped += 1
            continue

        conn.execute(
            'INSERT INTO software_apps (name, version, lab_id, availability) VALUES (?, ?, ?, ?)',
            (name, version, lab_id, 'available')
        )
        print(f'  ADD   {name} ({lab_id or "General"})')
        inserted += 1

    conn.commit()
    conn.close()
    print(f'\nDone! {inserted} added, {skipped} skipped.')

if __name__ == '__main__':
    seed()