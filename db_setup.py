import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Drop existing to prevent schema conflict mismatches
    cursor.execute("DROP TABLE IF EXISTS Users")
    cursor.execute("DROP TABLE IF EXISTS Units")
    cursor.execute("DROP TABLE IF EXISTS Drone_Models")
    cursor.execute("DROP TABLE IF EXISTS Distributed_Assets")
    cursor.execute("DROP TABLE IF EXISTS Inventory_Parts")
    cursor.execute("DROP TABLE IF EXISTS Manufacturing_Queue")
    cursor.execute("DROP TABLE IF EXISTS Transfer_Requests")
    cursor.execute("DROP TABLE IF EXISTS Receipt_Requests")

    # Units
    cursor.execute("CREATE TABLE Units (unit_id INTEGER PRIMARY KEY AUTOINCREMENT, unit_name TEXT UNIQUE, command_theater TEXT)")
    
    # Users
    cursor.execute("CREATE TABLE Users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, unit_id INTEGER, FOREIGN KEY(unit_id) REFERENCES Units(unit_id))")
    
    # Drone Catalog
    cursor.execute("CREATE TABLE Drone_Models (model_id INTEGER PRIMARY KEY AUTOINCREMENT, model_name TEXT UNIQUE, role_type TEXT, flight_time TEXT, payload_capacity TEXT, technical_specs TEXT)")
    
    # Distributed Assets with precise history logging metrics
    cursor.execute('''CREATE TABLE Distributed_Assets (
                        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT,
                        serial_number TEXT UNIQUE,
                        assigned_unit_id INTEGER,
                        status TEXT,
                        issue_date TEXT,
                        auth_letter TEXT,
                        FOREIGN KEY(assigned_unit_id) REFERENCES Units(unit_id))''')

    # Inventory Spares
    cursor.execute("CREATE TABLE Inventory_Parts (part_id INTEGER PRIMARY KEY AUTOINCREMENT, part_name TEXT UNIQUE, qty_available INTEGER, qty_demanded INTEGER, status TEXT)")
    
    # Production Line Queue
    cursor.execute("CREATE TABLE Manufacturing_Queue (job_id INTEGER PRIMARY KEY AUTOINCREMENT, drone_type TEXT, progress_percent INTEGER, est_timeline TEXT)")
    
    # Handover Channel (Unit to Unit via Commander)
    cursor.execute("CREATE TABLE Transfer_Requests (transfer_id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id INTEGER, from_unit_id INTEGER, to_unit_id INTEGER, status TEXT)")

    # NEW: Receipt Pipeline Channel (User Unit Logs Entry -> Admin Approves -> Appends to Fleet Logs)
    cursor.execute('''CREATE TABLE Receipt_Requests (
                        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT,
                        serial_number TEXT,
                        unit_id INTEGER,
                        arrival_date TEXT,
                        letter_number TEXT,
                        status TEXT)''')

    # Seed initial pristine telemetry parameters
    cursor.executescript('''
    INSERT INTO Units VALUES (1, 'Manufacturer HQ', 'Global'), (2, '74th Armored Brigade', 'Northern Command'), (3, '81st Artillery Division', 'Northern Command'), (4, 'Corps HQ', 'Northern Command');
    INSERT INTO Users VALUES (1, 'admin', 'admin123', 'Manufacturer', 1), (2, 'unit74', 'unit123', 'User_Unit', 2), (3, 'unit81', 'unit123', 'User_Unit', 3), (4, 'commander', 'cdr123', 'Corps_Commander', 4);
    INSERT INTO Drone_Models VALUES (1, 'Sentinel-X', 'Reconnaissance', '45 Mins', '2.5 KG', 'High-grade encrypted optical telemetry.'), (2, 'Striker-V2', 'Precision Loitering', '30 Mins', '5.0 KG', 'Thermal target tracking array.');
    INSERT INTO Distributed_Assets VALUES (1, 'Sentinel-X', 'SN-STNL-001', 2, 'Operational', '2026-05-12', 'A/4501/EME/LOG'), (2, 'Striker-V2', 'SN-STRK-099', 3, 'Operational', '2026-05-20', 'B/9912/EME/LOG');
    INSERT INTO Inventory_Parts VALUES (1, 'Electronic Speed Controllers (ESC)', 120, 10, 'Healthy'), (2, '5G Transceiver Modules', 8, 45, 'Critical Shortage');
    INSERT INTO Manufacturing_Queue VALUES (1, 'Sentinel-X (Batch #4)', 75, '3 Days'), (2, 'Striker-V2 (Batch #2)', 20, '14 Days');
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
