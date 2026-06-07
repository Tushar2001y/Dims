# pages/2_Distribution.py
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="DIMS - Distribution Ledger", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ ACCESS DENIED: SECURE LOG IN REQUIRED")
    st.stop()

st.title("🚛 FLEET DEPLOYMENT & LOGISTICS CONTROL")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- DATABASE SCHEMATIC ALIGNMENT CHECK ---
# Enforces matching structural signatures for tracking down to specific node indices
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
# Resolves and lists every child unit reporting down the chain from the user's login node index
def get_authorized_node_ids(user_node_id, role):
    if role == 'Admin':
        # Manufacturer Super Admin sees every asset node globally across the Corps
        res = conn.execute("SELECT node_id FROM Org_Structure").fetchall()
        return [r[0] for r in res]
    
    # Recursive Common Table Expression (CTE) to discover all descendant formations
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

auth_nodes = get_authorized_node_ids(st.session_state.node_id, st.session_state.role)


# --- ADMINISTRATIVE PIPELINE: REVIEW USER UNIT INBOUND SUBMISSIONS ---
if st.session_state.role == 'Admin':
    st.subheader("📥 PENDING INBOUND RECEIPT REQUESTS (ADMIN VERIFICATION)")
    pending_receipts = pd.read_sql_query("SELECT * FROM Receipt_Requests WHERE status='Pending Verification'", conn)
    
    if not pending_receipts.empty:
        for _, r_row in pending_receipts.iterrows():
            with st.container():
                st.info(f"Unit ID {r_row['unit_id']} reports receiving **{r_row['model_name']}** (S/N: {r_row['serial_number']}) on **{r_row['arrival_date']}** under Letter: **{r_row['letter_number']}**")
                rc1, rc2 = st.columns([1, 6])
                if rc1.button("APPROVE & COMMIT", key=f"app_rec_{r_row['receipt_id']}"):
                    cursor.execute("""
                        INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) 
                        VALUES (?, ?, ?, 'Operational', ?, ?)""",
                        (r_row['model_name'], r_row['serial_number'], r_row['unit_id'], r_row['arrival_date'], r_row['letter_number']))
                    
                    cursor.execute("UPDATE Receipt_Requests SET status='Approved' WHERE receipt_id=?", (r_row['receipt_id'],))
                    conn.commit()
                    st.success("Record permanently written to fleet distribution archives.")
                    st.rerun()
        st.divider()


# --- FORWARD DETAILED BREAKDOWN PER FORMATION UNIT ---
st.subheader("📋 SELECT FORMATION UNIT FOR GRANULAR DOSSIER")

# Generates placeholder strings dynamically based on the quantity of authorized visibility indices
placeholders = ",".join("?" for _ in auth_nodes)
unit_list = pd.read_sql_query(f"SELECT node_id, node_name FROM Org_Structure WHERE node_id IN ({placeholders})", conn, params=auth_nodes)

if not unit_list.empty:
    selected_node_id = st.selectbox("CHOOSE BRIGADE / FORMATION SECTOR COMPARTMENT", 
                                    options=unit_list['node_id'].tolist(), 
                                    format_func=lambda x: dict(zip(unit_list['node_id'], unit_list['node_name']))[x])

    st.markdown("### 📊 TABLEAU LOGISTICAL ANALYSIS")
    detailed_query = """SELECT model_name AS [Drone Model], serial_number AS [Serial Number], 
                               status AS [Operational Status], issue_date AS [Date Issued], 
                               auth_letter AS [Authority Letter reference] 
                        FROM Distributed_Assets WHERE assigned_unit_id = ?"""
    detailed_df = pd.read_sql_query(detailed_query, conn, params=(selected_node_id,))

    if not detailed_df.empty:
        st.dataframe(detailed_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No tracked hardware signatures currently mapped to this formation ledger.")
else:
    st.error("Logistical isolation fault: No authorized sector clearances allocated to this profile.")


# --- USER UNIT INBOUND SUBMISSION FORM ---
# Extends submission capability to any active, authenticated node level below Super Admin
if st.session_state.role != 'Admin':
    st.divider()
    st.subheader("📬 LOG NEW INBOUND DRONE RECEIPT")
    with st.form("inbound_receipt_form", clear_on_submit=True):
        st.markdown("<p style='color: #888;'>Submit physical handovers here. Changes will populate across command networks following Admin authentication.</p>", unsafe_allow_html=True)
        r_model = st.text_input("DRONE MODEL TYPE")
        r_sn = st.text_input("HARDWARE SERIAL NUMBER (S/N)")
        r_date = st.date_input("DATE OF RECEIPT")
        r_letter = st.text_input("AUTHORITY LETTER NUMBER REFERENCE")
        
        if st.form_submit_button("SUBMIT TO LOGISTICS COMMAND"):
            if r_model and r_sn and r_letter:
                cursor.execute("""
                    INSERT INTO Receipt_Requests (model_name, serial_number, unit_id, arrival_date, letter_number, status) 
                    VALUES (?,?,?,?,?, 'Pending Verification')""",
                    (r_model, r_sn, st.session_state.node_id, str(r_date), r_letter))
                conn.commit()
                st.toast("Receipt submitted to Admin for validation.")
            else:
                st.error("All metric tracking blocks must be completed.")

conn.close()
