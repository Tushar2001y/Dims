import sqlite3
import random
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # --- 1. RESET AND CREATE TABLES ---
    cursor.execute("DROP TABLE IF EXISTS Org_Structure")
    cursor.execute("DROP TABLE IF EXISTS Distributed_Assets")
    cursor.execute("DROP TABLE IF EXISTS Receipt_Requests")

    cursor.execute('''
        CREATE TABLE Org_Structure (
            node_id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_name TEXT UNIQUE NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES Org_Structure(node_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Distributed_Assets (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            assigned_unit_id INTEGER,
            status TEXT DEFAULT 'Operational',
            issue_date TEXT,
            auth_letter TEXT,
            FOREIGN KEY(assigned_unit_id) REFERENCES Org_Structure(node_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE Receipt_Requests (
            receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            serial_number TEXT NOT NULL,
            unit_id INTEGER,
            arrival_date TEXT,
            letter_number TEXT,
            status TEXT DEFAULT 'Pending Verification',
            FOREIGN KEY(unit_id) REFERENCES Org_Structure(node_id)
        )
    ''')

    # --- 2. BUILD THE EXPANDED COMMAND HIERARCHY ---
    # (node_name, parent_id). 9 Corps is ID 1.
    org_data = [
        ('9 Corps', None),             # ID 1
        
        # Divisions
        ('29 Div', 1),                 # ID 2
        ('39 Div', 1),                 # ID 3 (New)
        
        # Brigades under 29 Div
        ('A Bde', 2),                  # ID 4
        ('B Bde', 2),                  # ID 5
        ('C Bde', 2),                  # ID 6
        ('Arty Bde', 2),               # ID 7 (New)
        
        # Brigades under 39 Div
        ('X Bde', 3),                  # ID 8 (New)
        ('Y Bde', 3),                  # ID 9 (New)

        # Units under A Bde
        ('1st Infantry Bn', 4),        # ID 10
        ('2nd Infantry Bn', 4),        # ID 11
        
        # Units under B Bde
        ('5th Armored Regt', 5),       # ID 12 (New)
        ('9th Mechanized Inf', 5),     # ID 13 (New)
        
        # Units under C Bde
        ('11th Para SF', 6),           # ID 14 (New)
        ('3 EME Bn', 6),               # ID 15
        
        # Units under X Bde
        ('7th Infantry Bn', 8),        # ID 16 (New)
        ('4 EME Bn', 8)                # ID 17 (New)
    ]
    
    for name, parent in org_data:
        cursor.execute("INSERT INTO Org_Structure (node_name, parent_id) VALUES (?, ?)", (name, parent))

    # Helper function to grab the correct ID for dynamic deployment
    def get_unit_id(unit_name):
        cursor.execute("SELECT node_id FROM Org_Structure WHERE node_name=?", (unit_name,))
        res = cursor.fetchone()
        return res[0] if res else 1

    # --- 3. DYNAMICALLY GENERATE 120 DRONES ---
    # We will let the script drop assets across ALL units defined above
    target_units = [name for name, _ in org_data] 

    models = ['Navastra 51', 'Navastra 81']
    statuses = ['Operational', 'Operational', 'Operational', 'Operational', 'Maintenance', 'Awaiting Spares']

    assets_to_deploy = []
    
    for i in range(1, 121):
        model = random.choice(models)
        unit = random.choice(target_units)
        status = random.choice(statuses)
        
        prefix = "NV51" if model == "Navastra 51" else "NV81"
        sn = f"SN-{prefix}-26-{i:03d}"
        
        # Randomize issue dates over the last 90 days
        days_ago = random.randint(1, 90)
        issue_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        auth_letter = f"9C/LOG/A{random.randint(10, 99)}"
        
        assets_to_deploy.append((model, sn, get_unit_id(unit), status, issue_date, auth_letter))

    cursor.executemany('''
        INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', assets_to_deploy)

    # --- 4. SEED THE MAKER-CHECKER PIPELINES ---
    # Adding a couple of items into the Admin & Commander queues so your demo isn't empty
    mock_receipts = [
        ('Navastra 51', 'SN-NV51-26-901', get_unit_id('1st Infantry Bn'), '2026-06-20', '9C/LOG/B12', 'Pending Verification'),
        ('Navastra 81', 'SN-NV81-26-902', get_unit_id('11th Para SF'), '2026-06-21', '9C/LOG/B14', 'Pending_GSEM')
    ]
    cursor.executemany('''
        INSERT INTO Receipt_Requests (model_name, serial_number, unit_id, arrival_date, letter_number, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', mock_receipts)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
