# pages/3_Inventory.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="DIMS - Inventory & Assembly", layout="wide")

# --- UNIFIED TACTICAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; }
    .metric-card {
        background: #1a1c24; padding: 15px; border-radius: 4px; border-left: 4px solid #00d4ff; margin-bottom: 10px;
    }
    .status-critical { color: #ff4b4b; font-weight: bold; }
    .status-healthy { color: #00ea92; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ ACCESS DENIED: SECURE LOG IN REQUIRED")
    st.stop()

st.title("🛠️ WAREHOUSE INVENTORY & ASSEMBLY COMMAND")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- INITIALIZE INVENTORY TABLES ---
cursor.execute('''CREATE TABLE IF NOT EXISTS Spares_Inventory (
                    part_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_name TEXT UNIQUE,
                    qty_available INTEGER,
                    qty_demanded INTEGER,
                    status TEXT)''')

# Seed baseline spares components if completely empty
baseline_spares = [
    ("Electronic Speed Controllers (ESC)", 120, 10, "Healthy"),
    ("Carbon Fiber Propellers (Set)", 450, 0, "Healthy"),
    ("5G Transceiver Modules", 8, 45, "Critical Shortage")
]
for item in baseline_spares:
    cursor.execute("INSERT OR IGNORE INTO Spares_Inventory (part_name, qty_available, qty_demanded, status) VALUES (?,?,?,?)", item)
conn.commit()


# --- SECTION 1: LIVE COMPONENT STOCK LEVEL TRACKING ---
st.subheader("📦 COMPONENT & SPARE PARTS STOCK LEVELS")

# Query current stock metrics
spares_df = pd.read_sql_query("SELECT part_name AS [Part Nomenclature], qty_available AS [Available Qty], qty_demanded AS [Indent Demanded], status AS [Supply Status] FROM Spares_Inventory", conn)

# Render a clean, stylized component ledger table
if not spares_df.empty:
    st.dataframe(spares_df, use_container_width=True, hide_index=True)
else:
    st.info("No component parts inventory data discovered inside this logistics sector.")


# --- SECTION 2: SIMPLIFIED PRODUCTION PIPELINE (THE ASSEMBLY WORKBENCH) ---
st.divider()
st.subheader("⚙️ FACTORY FLOOR ASSEMBLY LINE")

if st.session_state.role == 'Admin':
    st.markdown("<p style='color: #888;'>Select a tactical platform profile below to build an asset. The workbench will automatically check component status and deduct materials upon assembly execution.</p>", unsafe_allow_html=True)
    
    # 1. Define standard hardware assembly bills of materials (BOM)
    platform_options = {
        "Sentinel-X": {
            "ESC": 1,
            "Propeller": 1,
            "5G": 1
        },
        "Striker-V2": {
            "ESC": 2,
            "Propeller": 2,
            "5G": 1
        }
    }
    
    col_select, col_action = st.columns([2, 1])
    
    with col_select:
        selected_platform = st.selectbox("SELECT TARGET PLATFORM FOR PRODUCTION", options=list(platform_options.keys()))
        serial_input = st.text_input("ASSIGN UNIQUE HARDWARE SERIAL NUMBER (S/N)", placeholder="e.g., SN-SETX-2026-009")
    
    # Fetch live counts to cross-verify against requirements
    stock = {}
    for row in conn.execute("SELECT part_name, qty_available FROM Spares_Inventory").fetchall():
        if "ESC" in row[0]: stock["ESC"] = row[1]
        elif "Propellers" in row[0]: stock["Propeller"] = row[1]
        elif "5G" in row[0]: stock["5G"] = row[1]
        
    # Check if the store can support the specific build recipe
    requirements = platform_options[selected_platform]
    can_assemble = (stock.get("ESC", 0) >= requirements["ESC"] and 
                    stock.get("Propeller", 0) >= requirements["Propeller"] and 
                    stock.get("5G", 0) >= requirements["5G"])
    
    with col_action:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔧 EXECUTE PLATFORM ASSEMBLY", use_container_width=True, disabled=not can_assemble):
            if not serial_input:
                st.error("Assembly halted: A clean serial number index must be provided.")
            else:
                # 2. Deduct components safely from inventory logs
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%ESC%'", (requirements["ESC"],))
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%Propellers%'", (requirements["Propeller"],))
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%5G%'", (requirements["5G"],))
                
                # Update status strings dynamically if thresholds have been breached
                cursor.execute("UPDATE Spares_Inventory SET status = 'Critical Shortage' WHERE qty_available < 10")
                
                # 3. Inject new completed platform directly into local factory inventory pool
                # By writing this under Unit ID '1' (or a factory hold pool), it's verified and ready to distribute on Page 2
                cursor.execute("INSERT OR IGNORE INTO Org_Structure (node_id, node_name, node_type) VALUES (1, 'Central Workshop Pool', 'Manufacturer')")
                
                cursor.execute("""
                    INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) 
                    VALUES (?, ?, 1, 'Ready for Issue', ?, 'Factory Production Output Log')""",
                    (selected_platform, serial_input, datetime.now().strftime("%Y-%m-%d")))
                
                conn.commit()
                st.toast(f"🎉 Successfully built {selected_platform} (S/N: {serial_input})!")
                st.rerun()
                
    # Display an intuitive breakdown of component allocation for the user
    st.markdown("#### 📑 Required Assembly Materials Recipe:")
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.metric("Electronic Speed Controllers", f"{requirements['ESC']} Unit", f"Warehouse Stock: {stock.get('ESC', 0)}")
    with rc2:
        st.metric("Propeller Set Components", f"{requirements['Propeller']} Set", f"Warehouse Stock: {stock.get('Propeller', 0)}")
    with rc3:
        st.metric("5G Handshake Modules", f"{requirements['5G']} Unit", f"Warehouse Stock: {stock.get('5G', 0)}")
        
    if not can_assemble:
        st.error("🚨 CRITICAL ALERT: Production Line frozen due to ingredient resource shortage. Check the inventory levels above.")

else:
    # Subordinate unit view: simply shows a clean read-only receipt verification log
    st.info("ℹ️ Production parameters are restricted to Admin Headquarters. Subordinate formations retain clear read-only validation of component reserves.")

conn.close()
