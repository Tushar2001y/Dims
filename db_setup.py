import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Drop existing tables to ensure clean schema update
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS Units")
    cursor.execute("DROP TABLE IF EXISTS Drone_Models")
    cursor.execute("DROP TABLE IF EXISTS Distributed_Assets")
    cursor.execute("DROP TABLE IF EXISTS Inventory_Parts")
    cursor.execute("DROP TABLE IF EXISTS Manufacturing_Queue")
    cursor.execute("DROP TABLE IF EXISTS Transfer_Requests")

    # 1. Units Table
    cursor.execute('''
    CREATE TABLE Units (
        unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_name TEXT UNIQUE,
        command_theater TEXT
    )''')

    # 2. Users Table
    cursor.execute('''
    CREATE TABLE Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        unit_id INTEGER,
        FOREIGN KEY(unit_id) REFERENCES Units(unit_id)
    )''')

    # 3. Drone Models Table (Brochure)
    cursor.execute('''
    CREATE TABLE Drone_Models (
        model_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT UNIQUE,
        role_type TEXT,
        flight_time TEXT,
        payload_capacity TEXT,
        technical_specs TEXT
    )''')

    # 4. Distributed Assets Table (Distribution List)
    cursor.execute('''
    CREATE TABLE Distributed_Assets (
        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT,
        serial_number TEXT UNIQUE,
        assigned_unit_id INTEGER,
        status TEXT,
        FOREIGN KEY(assigned_unit_id) REFERENCES Units(unit_id)
    )''')

    # 5. Inventory & Spares Table
    cursor.execute('''
    CREATE TABLE Inventory_Parts (
        part_id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_name TEXT UNIQUE,
        qty_available INTEGER,
        qty_demanded INTEGER,
        status TEXT
    )''')

    # 6. Manufacturing Queue Table
    cursor.execute('''
    CREATE TABLE Manufacturing_Queue (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        drone_type TEXT,
        progress_percent INTEGER,
        est_timeline TEXT
    )''')

    # 7. Transfer Requests Table (Corps Commander Pipeline)
    cursor.execute('''
    CREATE TABLE Transfer_Requests (
        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER,
        from_unit_id INTEGER,
        to_unit_id INTEGER,
        status TEXT,
        FOREIGN KEY(asset_id) REFERENCES Distributed_Assets(asset_id),
        FOREIGN KEY(from_unit_id) REFERENCES Units(unit_id),
        FOREIGN KEY(to_unit_id) REFERENCES Units(unit_id)
    )''')

    # --- Populate Dummy / Seed Data ---
    cursor.executescript('''
    INSERT INTO Units (unit_id, unit_name, command_theater) VALUES 
        (1, 'Manufacturer HQ', 'Global'),
        (2, '74th Armored Brigade', 'Northern Command'),
        (3, '81st Artillery Division', 'Northern Command'),
        (4, 'Corps HQ', 'Northern Command');

    INSERT INTO Users (username, password, role, unit_id) VALUES 
        ('admin', 'admin123', 'Manufacturer', 1),
        ('unit74', 'unit123', 'User_Unit', 2),
        ('unit81', 'unit123', 'User_Unit', 3),
        ('commander', 'cdr123', 'Corps_Commander', 4);

    INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) VALUES
        ('Sentinel-X', 'Reconnaissance', '45 Mins', '2.5 KG', 'High-grade optical zoom, 5G enabled encryption.'),
        ('Striker-V2', 'Precision Loitering', '30 Mins', '5.0 KG', 'Integrated thermal tracking, terminal guidance payload.');

    INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status) VALUES
        ('Sentinel-X', 'SN-STNL-001', 2, 'Operational'),
        ('Sentinel-X', 'SN-STNL-002', 2, 'Under Repair'),
        ('Striker-V2', 'SN-STRK-099', 3, 'Operational');

    INSERT INTO Inventory_Parts (part_name, qty_available, qty_demanded, status) VALUES
        ('Electronic Speed Controllers (ESC)', 120, 10, 'Healthy'),
        ('Carbon Fiber Propellers (Set)', 450, 0, 'Healthy'),
        ('5G Transceiver Modules', 8, 45, 'Critical Shortage');

    INSERT INTO Manufacturing_Queue (drone_type, progress_percent, est_timeline) VALUES
        ('Sentinel-X (Batch #4)', 75, '3 Days'),
        ('Striker-V2 (Batch #2)', 20, '14 Days');
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
