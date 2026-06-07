# pages/3_Inventory.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="DIMS - Inventory", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    .inventory-table { background-color: #ffffff; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("🛠️ Warehouse Inventory Management")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

st.subheader("📦 Component & Spare Parts Stock Levels")
spares_df = pd.read_sql_query("SELECT part_name AS [Component Nomenclature], qty_available AS [Available Quantity], qty_demanded AS [Indent Demanded], status AS [Supply Integrity] FROM Spares_Inventory", conn)

if not spares_df.empty:
    st.dataframe(spares_df, use_container_width=True, hide_index=True)
else:
    st.info("No components listed in this warehouse section.")

if st.session_state.role == 'Admin':
    st.divider()
    st.subheader("⚙️ Factory Assembly Workbench")
    
    platform_options = {
        "Sentinel-X": {"ESC": 1, "Propeller": 1, "5G": 1},
        "Striker-V2": {"ESC": 2, "Propeller": 2, "5G": 1}
    }
    
    col_sel, col_act = st.columns([2, 1])
    with col_sel:
        selected_platform = st.selectbox("Target Construction Variant Model", options=list(platform_options.keys()))
        serial_input = st.text_input("Assign Final Unique Serial Number Profile")
        
    stock = {}
    for row in conn.execute("SELECT part_name, qty_available FROM Spares_Inventory").fetchall():
        if "ESC" in row[0]: stock["ESC"] = row[1]
        elif "Propellers" in row[0]: stock["Propeller"] = row[1]
        elif "5G" in row[0]: stock["5G"] = row[1]
        
    recipe = platform_options[selected_platform]
    can_build = (stock.get("ESC", 0) >= recipe["ESC"] and stock.get("Propeller", 0) >= recipe["Propeller"] and stock.get("5G", 0) >= recipe["5G"])
    
    with col_act:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Assemble Selected Platform", use_container_width=True, disabled=not can_build):
            if serial_input:
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%ESC%'", (recipe["ESC"],))
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%Propellers%'", (recipe["Propeller"],))
                cursor.execute("UPDATE Spares_Inventory SET qty_available = qty_available - ? WHERE part_name LIKE '%5G%'", (recipe["5G"],))
                
                # Default seed warehouse holder node input
                cursor.execute("INSERT OR IGNORE INTO Org_Structure (node_id, node_name, node_type) VALUES (1, 'Central Workshop Pool', 'Manufacturer')")
                cursor.execute("""
                    INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) 
                    VALUES (?, ?, 1, 'Ready for Issue', ?, 'Factory Assembly Line Output')""",
                    (selected_platform, serial_input, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.toast("Platform assembled successfully.")
                st.rerun()
            else:
                st.error("A clear unique serial identifier is mandatory.")

    st.markdown("#### Components Allocation Requirements Checklist:")
    c1, c2, c3 = st.columns(3)
    c1.metric("ESCs Needed", f"{recipe['ESC']} Unit", f"In Stock: {stock.get('ESC', 0)}")
    c2.metric("Propellers Needed", f"{recipe['Propeller']} Set", f"In Stock: {stock.get('Propeller', 0)}")
    c3.metric("5G Handshakes Needed", f"{recipe['5G']} Unit", f"In Stock: {stock.get('5G', 0)}")

conn.close()
