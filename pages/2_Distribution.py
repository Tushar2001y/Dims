import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Distribution Ledger", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2, h3 { color: #00d4ff !important; }</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.stop()

st.title("🚛 FLEET DEPLOYMENT & LOGISTICS CONTROL")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- ADMINISTRATIVE PIPELINE: REVIEW USER UNIT INBOUND SUBMISSIONS ---
if st.session_state.role == 'Manufacturer':
    st.subheader("📥 PENDING INBOUND RECEIPT REQUESTS (REQUIRING ADMIN VERIFICATION)")
    pending_receipts = pd.read_sql_query("SELECT * FROM Receipt_Requests WHERE status='Pending Verification'", conn)
    
    if not pending_receipts.empty:
        for _, r_row in pending_receipts.iterrows():
            with st.container():
                st.info(f"Unit ID {r_row['unit_id']} reports receiving **{r_row['model_name']}** (S/N: {r_row['serial_number']}) on **{r_row['arrival_date']}** under Letter: **{r_row['letter_number']}**")
                rc1, rc2 = st.columns([1, 6])
                if rc1.button("APPROVE & COMMIT", key=f"app_rec_{r_row['receipt_id']}"):
                    cursor.execute("INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) VALUES (?, ?, ?, 'Operational', ?, ?)",
                                   (r_row['model_name'], r_row['serial_number'], r_row['unit_id'], r_row['arrival_date'], r_row['letter_number']))
                    cursor.execute("UPDATE Receipt_Requests SET status='Approved' WHERE receipt_id=?", (r_row['receipt_id'],))
                    conn.commit()
                    st.success("Record permanently written to fleet distribution archives.")
                    st.rerun()
        st.divider()

# --- FORWARD DETAILED BREAKDOWN PER FORMATION UNIT ---
st.subheader("📋 SELECT FORMATION UNIT FOR GRANULAR DOSSIER")
unit_list = pd.read_sql_query("SELECT unit_id, unit_name FROM Units WHERE unit_id != 1", conn)
selected_unit_id = st.selectbox("CHOOSE BRIGADE / FORMATION", options=unit_list['unit_id'].tolist(), format_func=lambda x: dict(zip(unit_list['unit_id'], unit_list['unit_name']))[x])

st.markdown("### 📊 TABLEAU LOGISTICAL ANALYSIS")
detailed_query = """SELECT model_name AS [Drone Model], serial_number AS [Serial Number], 
                           status AS [Operational Status], issue_date AS [Date Issued], 
                           auth_letter AS [Authority Letter reference] 
                    FROM Distributed_Assets WHERE assigned_unit_id = ?"""
detailed_df = pd.read_sql_query(detailed_query, conn, params=(selected_unit_id,))

if not detailed_df.empty:
    st.dataframe(detailed_df, use_container_width=True, hide_index=True)
else:
    st.warning("No tracked hardware signatures currently mapped to this formation ledger.")

# --- USER UNIT INBOUND SUBMISSION FORM ---
if st.session_state.role == 'User_Unit':
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
                cursor.execute("INSERT INTO Receipt_Requests (model_name, serial_number, unit_id, arrival_date, letter_number, status) VALUES (?,?,?,?,?, 'Pending Verification')",
                               (r_model, r_sn, st.session_state.unit_id, str(r_date), r_letter))
                conn.commit()
                st.toast("Receipt submitted to Admin for validation.")
            else:
                st.error("All metric tracking blocks must be completed.")

conn.close()
