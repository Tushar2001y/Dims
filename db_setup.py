import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Dropping tables to ensure clean schema update
    tables = ["Users", "Units", "Drone_Models", "Distributed_Assets", "Inventory_Parts", "Manufacturing_Queue", "Receipt_Requests"]
    for table in tables: cursor.execute(f"DROP TABLE IF EXISTS {table}")

    cursor.execute("CREATE TABLE Units (unit_id INTEGER PRIMARY KEY, unit_name TEXT, command_theater TEXT)")
    cursor.execute("CREATE TABLE Users (user_id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, unit_id INTEGER)")
    cursor.execute("CREATE TABLE Drone_Models (model_id INTEGER PRIMARY KEY, model_name TEXT, role_type TEXT, flight_time TEXT, payload_capacity TEXT, technical_specs TEXT, image_path TEXT)")
    cursor.execute("CREATE TABLE Distributed_Assets (asset_id INTEGER PRIMARY KEY, model_name TEXT, serial_number TEXT, assigned_unit_id INTEGER, status TEXT, issue_date TEXT, auth_letter TEXT)")
    cursor.execute("CREATE TABLE Manufacturing_Queue (job_id INTEGER PRIMARY KEY, drone_type TEXT, progress_percent INTEGER, est_timeline TEXT)")
    cursor.execute("CREATE TABLE Inventory_Parts (part_id INTEGER PRIMARY KEY, part_name TEXT, qty_available INTEGER, status TEXT)")
    cursor.execute("CREATE TABLE Receipt_Requests (receipt_id INTEGER PRIMARY KEY, model_name TEXT, serial_number TEXT, unit_id INTEGER, arrival_date TEXT, letter_number TEXT, status TEXT)")

    cursor.executescript('''
        INSERT INTO Units VALUES (1, 'Manufacturer HQ', 'Global'), (2, '74th Armored Brigade', 'Northern'), (3, 'Corps HQ', 'Northern');
        INSERT INTO Users VALUES (1, 'admin', 'admin123', 'Manufacturer', 1), (2, 'unit74', 'unit123', 'User_Unit', 2), (3, 'commander', 'cdr123', 'Corps_Commander', 3);
        INSERT INTO Drone_Models VALUES (1, 'Sentinel-X', 'Recon', '45m', '2kg', 'High-res optical', 'None');
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__": init_db()
