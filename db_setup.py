# db_setup.py
import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # --- 1. CLEAN SLATE (Optional but recommended for a fresh seed) ---
    tables = ['Org_Structure', 'Users', 'Distributed_Assets', 'Receipt_Requests', 'Spares_Inventory', 'Drone_Models']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # --- 2. STRUCTURAL TABLES ---
    cursor.execute('''CREATE TABLE Org_Structure (
                        node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_name TEXT UNIQUE,
                        node_type TEXT,
                        parent_id INTEGER)''')
    
    cursor.execute('''CREATE TABLE Users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        node_id INTEGER)''')
    
    cursor.execute('''CREATE TABLE Distributed_Assets (
                        asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT,
                        serial_number TEXT,
                        assigned_unit_id INTEGER,
                        status TEXT,
                        issue_date TEXT,
                        auth_letter TEXT)''')

    cursor.execute('''CREATE TABLE Receipt_Requests (
                        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT,
                        serial_number TEXT,
                        unit_id INTEGER,
                        arrival_date TEXT,
                        letter_number TEXT,
                        status TEXT)''')
                        
    cursor.execute('''CREATE TABLE Spares_Inventory (
                        part_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        part_name TEXT UNIQUE,
                        qty_available INTEGER,
                        qty_demanded INTEGER,
                        status TEXT)''')

    cursor.execute('''CREATE TABLE Drone_Models (
                        model_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT UNIQUE,
                        role_type TEXT,
                        flight_time TEXT,
                        payload_capacity TEXT,
                        technical_specs TEXT)''')

    # --- 3. SEED 9 CORPS HIERARCHY (Down to User Units) ---
    formations = [
        # Base Command
        ("9 Corps", "Corps", None),
        
        # Divisions
        ("29 Div", "Division", "9 Corps"),
        ("6002(I) Div", "Division", "9 Corps"),
        ("26 Div", "Division", "9 Corps"),
        
        # Independent Brigades under Corps
        ("16(I) Bde", "Brigade", "9 Corps"),
        ("7009 Bde", "Brigade", "9 Corps"),
        
        # Brigades under 29 Div
        ("A Bde", "Brigade", "29 Div"),
        ("B Bde", "Brigade", "29 Div"),
        ("C Bde", "Brigade", "29 Div"),
        
        # Brigades under 6002(I) Div
        ("D Bde", "Brigade", "6002(I) Div"),
        ("E Bde", "Brigade", "6002(I) Div"),
        
        # Brigades under 26 Div
        ("F Bde", "Brigade", "26 Div"),
        
        # --- USER UNITS ---
        # Units under A Bde
        ("1st Infantry Bn", "User Unit", "A Bde"),
        ("2nd Infantry Bn", "User Unit", "A Bde"),
        # Units under D Bde
        ("5th Armored Regt", "User Unit", "D Bde"),
        ("6th Armored Regt", "User Unit", "D Bde"),
        # Units under F Bde
        ("9th Mechanized Inf", "User Unit", "F Bde"),
        # Units under 16(I) Bde
        ("11th Para SF", "User Unit", "16(I) Bde"),
        ("12th Para SF", "User Unit", "16(I) Bde"),
        # Central node for manufacturing/holding
        ("Central Workshop Pool", "Manufacturer", "9 Corps") 
    ]
    
    for name, n_type, parent in formations:
        p_id = None
        if parent:
            cursor.execute("SELECT node_id FROM Org_Structure WHERE node_name=?", (parent,))
            p_row = cursor.fetchone()
            p_id = p_row[0] if p_row else None
        cursor.execute("INSERT OR IGNORE INTO Org_Structure (node_name, node_type, parent_id) VALUES (?, ?, ?)", (name, n_type, p_id))
    
    # --- 4. PROVISION ADMIN ACCOUNT ---
    cursor.execute("SELECT node_id FROM Org_Structure WHERE node_name='9 Corps'")
    corps_node = cursor.fetchone()[0]
    cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, node_id) VALUES ('admin', 'admin123', 'Admin', ?)", (corps_node,))
    
    # --- 5. REGISTER DRONE PLATFORMS ---
    cursor.execute("INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) VALUES ('Navastra 51', 'Surveillance & Target Acquisition', '60 Mins', '2.5 kg', 'EO/IR sensor payload, encrypted 5G telemetry, anti-jamming GPS module.')")
    cursor.execute("INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) VALUES ('Navastra 81', 'Heavy Payload / Loitering Munition', '40 Mins', '12 kg', 'Terminal guidance, extended range antenna, modular payload bay.')")
    
    # --- 6. DISTRIBUTE ASSETS TO USER UNITS ---
    # Helper to fetch Unit ID safely
    def get_unit_id(unit_name):
        cursor.execute("SELECT node_id FROM Org_Structure WHERE node_name=?", (unit_name,))
        res = cursor.fetchone()
        return res[0] if res else 1

    # Navastra 51 Distribution (Surveillance)
    assets_to_deploy = [
        ('Navastra 51', 'SN-NV51-26-001', get_unit_id('1st Infantry Bn'), 'Operational', '2026-05-10', '9C/LOG/A01'),
        ('Navastra 51', 'SN-NV51-26-002', get_unit_id('1st Infantry Bn'), 'Operational', '2026-05-10', '9C/LOG/A01'),
        ('Navastra 51', 'SN-NV51-26-003', get_unit_id('2nd Infantry Bn'), 'Operational', '2026-05-14', '9C/LOG/A02'),
        ('Navastra 51', 'SN-NV51-26-004', get_unit_id('9th Mechanized Inf'), 'Maintenance', '2026-03-22', '9C/LOG/F01'),
        ('Navastra 51', 'SN-NV51-26-005', get_unit_id('11th Para SF'), 'Operational', '2026-01-15', '9C/LOG/SF1'),
    ]
    
    # Navastra 81 Distribution (Heavy/Kamikaze)
    assets_to_deploy += [
        ('Navastra 81', 'SN-NV81-26-001', get_unit_id('5th Armored Regt'), 'Operational', '2026-06-01', '9C/LOG/D01'),
        ('Navastra 81', 'SN-NV81-26-002', get_unit_id('6th Armored Regt'), 'Operational', '2026-06-01', '9C/LOG/D01'),
        ('Navastra 81', 'SN-NV81-26-003', get_unit_id('11th Para SF'), 'Operational', '2026-02-18', '9C/LOG/SF2'),
        ('Navastra 81', 'SN-NV81-26-004', get_unit_id('12th Para SF'), 'Operational', '2026-02-18', '9C/LOG/SF2'),
        ('Navastra 81', 'SN-NV81-26-005', get_unit_id('Central Workshop Pool'), 'Ready for Issue', '2026-06-05', 'Factory Assembly Log'),
    ]

    for asset in assets_to_deploy:
        cursor.execute("INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) VALUES (?,?,?,?,?,?)", asset)
    
    # --- 7. SEED BASELINE SPARES ---
    baseline_spares = [
        ("Navastra 51 Flight Controllers", 45, 0, "Healthy"),
        ("Navastra 81 Heavy Duty ESCs", 120, 10, "Healthy"),
        ("Carbon Fiber Propellers (Set)", 350, 0, "Healthy"),
        ("5G Telemetry Transceivers", 12, 25, "Critical Shortage"),
        ("Payload Release Mechanisms", 68, 5, "Healthy")
    ]
    for part, qty, dem, stat in baseline_spares:
        cursor.execute("INSERT INTO Spares_Inventory (part_name, qty_available, qty_demanded, status) VALUES (?,?,?,?)", (part, qty, dem, stat))

    conn.commit()
    conn.close()
    print("Database successfully built and populated with Navastra fleet configurations.")

if __name__ == "__main__":
    init_db()
