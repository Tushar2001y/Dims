# pages/2_Distribution.py
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="DIMS - Fleet Deployment", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    .management-block {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("🚛 Fleet Deployment & Logistics Control")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

current_node_id = st.session_state.get('node_id', 1)
current_role = st.session_state.get('role', 'User_Unit')

# Pure Python Hierarchy Descendant Resolver Loop
def get_authorized_node_ids(user_node_id, role):
    if role == 'Admin':
        res = cursor.execute("SELECT node_id FROM Org_Structure").fetchall()
        return [r[0] for r in res]
    
    user_node_id = int(user_node_id)
    all_nodes = cursor.execute("SELECT node_id, parent_id FROM Org_Structure").fetchall()
    
    tree_map = {}
    for n_id, p_id in all_nodes:
        if p_id is not None:
            tree_map.setdefault(int(p_id), []).append(int(n_id))
            
    authorized_ids = [user_node_id]
    queue = [user_node_id]
    while queue:
        current = queue.pop(0)
        if current in tree_map:
            for child in tree_map[current]:
                if child not in authorized_ids:
                    authorized_ids.append(child)
                    queue.append(child)
    return authorized_ids

auth_nodes = get_authorized_node_ids(current_node_id, current_role)

# --- WORKFLOW 1: ADMIN MANAGEMENT SUBMISSION PIPELINE ---
if current_role == 'Admin':
    st.subheader("📥 Pending Inbound Receipt Requests (Requiring Admin Verification)")
    
    query_pending = """
        SELECT r.receipt_id, r.model_name, r.serial_number, o.node_name, r.arrival_date, r.letter_number 
        FROM Receipt_Requests r
        JOIN Org_Structure o ON r.unit_id = o.node_id
        WHERE r.status = 'Pending Verification'
    """
    pending_df = pd.read_sql_query(query_pending, conn)
    
    if not pending_df.empty:
        for idx, row in pending_df.iterrows():
            st.markdown("<div class='management-block'>", unsafe_allow_html=True)
            st.write(f"**Formation:** {row['node_name']} | **Model:** {row['model_name']} | **S/N:** {row['serial_number']}")
            st.write(f"**Letter Reference:** {row['letter_number']} | **Date Arrived:** {row['arrival_date']}")
            
            c1, c2, _ = st.columns([1.5, 1.5, 7])
            if c1.button("Approve Entry", key=f"app_rc_{row['receipt_id']}_{idx}", use_container_width=True):
                cursor.execute("""
                    INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) 
                    VALUES (?, ?, (SELECT node_id FROM Org_Structure WHERE node_name=?), 'Operational', ?, ?)""",
                    (row['model_name'], row['serial_number'], row['node_name'], row['arrival_date'], row['letter_number']))
                cursor.execute("UPDATE Receipt_Requests SET status='Approved' WHERE receipt_id=?", (row['receipt_id'],))
                conn.commit()
                st.rerun()
            if c2.button("Reject Request", key=f"rej_rc_{row['receipt_id']}_{idx}", use_container_width=True):
                cursor.execute("UPDATE Receipt_Requests SET status='Rejected' WHERE receipt_id=?", (row['receipt_id'],))
                conn.commit()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No incoming field unit receipt items require confirmation.")
    st.divider()

# --- WORKFLOW 2: DYNAMIC READ-ONLY GRID DOSSIER ---
st.subheader("📋 Select Formation Unit for Granular Dossier")

if auth_nodes:
    placeholders = ",".join("?" for _ in auth_nodes)
    unit_list = pd.read_sql_query(f"SELECT node_id, node_name FROM Org_Structure WHERE node_id IN ({placeholders})", conn, params=auth_nodes)

    if not unit_list.empty:
        selected_unit_id = st.selectbox(
            "Choose Brigade / Formation", 
            options=unit_list['node_id'].tolist(), 
            format_func=lambda x: dict(zip(unit_list['node_id'], unit_list['node_name']))[x]
        )

        st.markdown("### 📊 Tableau Logistical Analysis")
        
        # FIXED: Cast the selection parameter safely to an explicit primitive type integer inside tuple mapping
        detailed_query = """SELECT model_name AS [Drone Model], serial_number AS [Serial Number], 
                                   status AS [Operational Status], issue_date AS [Date Issued], 
                                   auth_letter AS [Authority Letter Reference] 
                            FROM Distributed_Assets WHERE assigned_unit_id = ?"""
        detailed_df = pd.read_sql_query(detailed_query, conn, params=(int(selected_unit_id),))

        if not detailed_df.empty:
            st.dataframe(detailed_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No tracked hardware signatures currently mapped to this selection.")
    else:
        st.error("Logistical isolation fault.")
else:
    st.error("No authorized sector clearances allocated.")

# --- WORKFLOW 3: FIELD RECONNAISSANCE FORM (HIDDEN FROM ADMIN) ---
if current_role != 'Admin':
    st.divider()
    st.subheader("📬 Log New Inbound Drone Receipt")
    with st.form("inbound_receipt_form", clear_on_submit=True):
        r_model = st.text_input("Drone Model Type")
        r_sn = st.text_input("Hardware Serial Number (S/N)")
        r_date = st.date_input("Date of Receipt")
        r_letter = st.text_input("Authority Letter Number Reference")
        
        if st.form_submit_button("Submit to Logistics Command", use_container_width=True):
            if r_model and r_sn and r_letter:
                cursor.execute("""
                    INSERT INTO Receipt_Requests (model_name, serial_number, unit_id, arrival_date, letter_number, status) 
                    VALUES (?,?,?,?,?, 'Pending Verification')""",
                    (r_model, r_sn, current_node_id, str(r_date), r_letter))
                conn.commit()
                st.toast("Receipt forwarded to Admin.")
            else:
                st.error("All parameter blocks are mandatory.")

conn.close()
