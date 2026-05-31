import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Distribution & Deployment", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .approval-card {
        background: #1a1c24;
        border: 1px solid #ff4b4b;
        padding: 20px;
        margin-bottom: 10px;
    }
    h1, h2 { color: #00d4ff !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.stop()

st.title("🚛 ASSET DISTRIBUTION & LOGISTICS")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- CORPS CDR APPROVAL SECTION ---
if st.session_state.role == 'Corps_Commander':
    st.subheader("🛡️ PENDING ASSET HANDOVERS (HQ APPROVAL)")
    reqs = pd.read_sql_query('''
        SELECT t.transfer_id, d.serial_number, u1.unit_name as FromUnit, u2.unit_name as ToUnit 
        FROM Transfer_Requests t JOIN Distributed_Assets d ON t.asset_id = d.asset_id
        JOIN Units u1 ON t.from_unit_id = u1.unit_id JOIN Units u2 ON t.to_unit_id = u2.unit_id
        WHERE t.status = 'Pending' ''', conn)
    
    if not reqs.empty:
        for _, row in reqs.iterrows():
            st.markdown(f"""<div class='approval-card'>
                <b>REQUEST ID:</b> {row['transfer_id']} | <b>ASSET:</b> {row['serial_number']}<br>
                <b>TRANSFER:</b> {row['FromUnit']} ➔ {row['ToUnit']}
                </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 6])
            if c1.button("APPROVE", key=f"a_{row['transfer_id']}"):
                cursor.execute("UPDATE Distributed_Assets SET assigned_unit_id = (SELECT to_unit_id FROM Transfer_Requests WHERE transfer_id=?), status='Operational' WHERE asset_id = (SELECT asset_id FROM Transfer_Requests WHERE transfer_id=?)", (row['transfer_id'], row['transfer_id']))
                cursor.execute("UPDATE Transfer_Requests SET status='Approved' WHERE transfer_id=?", (row['transfer_id'],))
                conn.commit()
                st.rerun()
    else:
        st.info("NO PENDING RE-ALLOCATION REQUESTS.")

# --- DISTRIBUTION LOGS ---
st.subheader("📊 GLOBAL DEPLOYMENT LOG")
if st.session_state.role in ['Manufacturer', 'Corps_Commander']:
    query = "SELECT d.serial_number, d.model_name, u.unit_name, d.status FROM Distributed_Assets d JOIN Units u ON d.assigned_unit_id = u.unit_id"
    df = pd.read_sql_query(query, conn)
else:
    query = "SELECT d.serial_number, d.model_name, u.unit_name, d.status FROM Distributed_Assets d JOIN Units u ON d.assigned_unit_id = u.unit_id WHERE d.assigned_unit_id = ?"
    df = pd.read_sql_query(query, conn, params=(st.session_state.unit_id,))

st.dataframe(df, use_container_width=True, hide_index=True)

# --- USER UNIT ACTIONS ---
if st.session_state.role == 'User_Unit':
    st.divider()
    with st.expander("🛠️ REPORT ASSET STATUS / INITIATE HANDOVER"):
        target_sn = st.selectbox("SELECT ASSET SN", df['serial_number'].tolist())
        action = st.radio("ACTION", ["Update Status", "Request Handover"])
        if action == "Update Status":
            new_stat = st.selectbox("NEW STATUS", ["Operational", "Under Repair", "Broken"])
            if st.button("SYNC STATUS"):
                cursor.execute("UPDATE Distributed_Assets SET status=? WHERE serial_number=?", (new_stat, target_sn))
                conn.commit()
                st.rerun()
        else:
            units = cursor.execute("SELECT unit_id, unit_name FROM Units WHERE unit_id NOT IN (1, ?, 4)", (st.session_state.unit_id,)).fetchall()
            target_unit = st.selectbox("RECIPIENT UNIT", options=[u[0] for u in units], format_func=lambda x: dict(units)[x])
            if st.button("SEND TO CORPS CDR FOR APPROVAL"):
                a_id = cursor.execute("SELECT asset_id FROM Distributed_Assets WHERE serial_number=?", (target_sn,)).fetchone()[0]
                cursor.execute("INSERT INTO Transfer_Requests (asset_id, from_unit_id, to_unit_id, status) VALUES (?,?,?, 'Pending')", (a_id, st.session_state.unit_id, target_unit))
                cursor.execute("UPDATE Distributed_Assets SET status='HANDOVER PENDING' WHERE asset_id=?", (a_id,))
                conn.commit()
                st.rerun()

conn.close()
