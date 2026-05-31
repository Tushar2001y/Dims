import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Units (
        unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_name TEXT,
        command_theater TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        unit_id INTEGER,
        FOREIGN KEY(unit_id) REFERENCES Units(unit_id)
    )''')

    cursor.executescript('''
    INSERT OR IGNORE INTO Units (unit_id, unit_name, command_theater) VALUES 
        (1, 'Manufacturer HQ', 'Global'),
        (2, '74th Armored Brigade', 'Northern Command'),
        (3, 'Corps HQ', 'Northern Command');

    INSERT OR IGNORE INTO Users (username, password, role, unit_id) VALUES 
        ('admin', 'admin123', 'Manufacturer', 1),
        ('unit74', 'unit123', 'User_Unit', 2),
        ('commander', 'cdr123', 'Corps_Commander', 3);
    ''')
    conn.commit()
    conn.close()
