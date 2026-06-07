# pages/2_Distribution.py
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="DIMS - Distribution Ledger", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

# 1. ABSOLUTE SECURITY ACCESS CHECK (Must happen first)
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ ACCESS DENIED: SECURE LOG IN REQUIRED")
    st.stop()

st.title("🚛 FLEET DEPLOYMENT & LOGISTICS CONTROL")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- DATABASE SCHEMATIC ALIGNMENT CHECK ---
cursor.execute('''CREATE TABLE IF NOT EXISTS Distributed_Assets (
                    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    serial_number TEXT,
                    assigned_unit_id INTEGER,
                    status TEXT,
                    issue_date TEXT,
                    auth_letter TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Receipt_Requests (
                    receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    serial_number TEXT,
                    unit_id INTEGER,
                    arrival_date TEXT,
                    letter_number TEXT,
                    status TEXT)''')
conn.commit()


# --- RECURSIVE SUB-TREE SECURITY ENGINE ---
def get_authorized_node_ids(user_node_id, role):
    if role == 'Admin':
        res = conn.execute("SELECT node_id FROM Org_Structure").fetchall()
        return [r[0] for r in res]
    
    query = """
    WITH RECURSIVE SubTree(node_id) AS (
        SELECT node_id FROM Org_Structure WHERE node_id = ?
        UNION ALL
        SELECT o.node_id FROM Org_Structure o JOIN SubTree s ON o.parent_id = s.node_id
    )
    SELECT node_id FROM SubTree;
    """
    res = conn.execute(query, (user_node_id,)).fetchall()
    return [r[0] for r in res]

# 2. SAFE VARIABLE EXTRACTION (Guaranteed to exist now because of st.stop() above)
current_node_id = st.session_state.get('node_id', 1)
current_role = st.session_state.get('role', 'User_Unit')

auth_nodes = get_authorized_node_ids(current_node_id, current_role)

# --- ADMINISTRATIVE PIPELINE: REVIEW USER UNIT INBOUND SUBMISSIONS ---
if current_role == 'Admin':
    st.subheader("📥 PENDING INBOUND RECEIPT REQUESTS (ADMIN VERIFICATION)")
    # ... (Rest of your existing Admin verification code runs exactly the same here)
