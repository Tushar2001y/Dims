import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Distribution", layout="wide")
st.title("🚛 DISTRIBUTION TABLEAU")
conn = sqlite3.connect('database.db')

# Unit Selection for Detail View
unit_data = pd.read_sql_query("SELECT unit_id, unit_name FROM Units WHERE unit_id != 1", conn)
target_unit = st.selectbox("SELECT FORMATION FOR DETAILED DOSSIER", options=unit_data['unit_id'].tolist(), format_func=lambda x: dict(zip(unit_data.unit_id, unit_data.unit_name))[x])

# The Tableau (Detailed Dataframe)
query = "SELECT model_name, serial_number, status, issue_date, auth_letter FROM Distributed_Assets WHERE assigned_unit_id = ?"
df = pd.read_sql_query(query, conn, params=(target_unit,))

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No active assets currently deployed to this unit.")

# User Unit Receipt Reporting
if st.session_state.role == 'User_Unit':
    st.divider()
    with st.form("receipt"):
        st.subheader("📬 LOG NEW RECEIPT")
        m = st.text_input("Model")
        sn = st.text_input("Serial Number")
        let = st.text_input("Auth Letter No.")
        if st.form_submit_button("SUBMIT FOR ADMIN APPROVAL"):
            conn.execute("INSERT INTO Receipt_Requests (model_name, serial_number, unit_id, letter_number, status) VALUES (?,?,?,?,'Pending')", (m, sn, st.session_state.unit_id, let))
            conn.commit()
            st.success("Request sent to HQ.")
conn.close()
