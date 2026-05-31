import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventory Management", layout="wide")

st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2 { color: #00d4ff !important; }</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or st.session_state.role == 'User_Unit':
    st.error("🚫 RESTRICTED: LOGISTICS COMMAND ONLY")
    st.stop()

st.title("⚙️ INVENTORY & PRODUCTION COMMAND")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

category = st.radio("SELECT CATEGORY", ["PRODUCTION LINE", "SPARES INVENTORY"], horizontal=True)
st.divider()

mode = st.radio("SELECT MODE", ["OBSERVE & REPORT", "UPDATE RECORDS"], horizontal=True)

if category == "PRODUCTION LINE":
    if mode == "OBSERVE & REPORT":
        st.subheader("🏭 ASSEMBLY LINE TELEMETRY")
        mq = pd.read_sql_query("SELECT drone_type as [Model], progress_percent as [Progress], est_timeline as [Timeline] FROM Manufacturing_Queue", conn)
        for _, row in mq.iterrows():
            st.write(f"**{row['Model']}** | {row['Timeline']}")
            st.progress(row['Progress'])
    else:
        st.subheader("🛠️ PRODUCTION UPDATE")
        update_type = st.selectbox("UPDATE TYPE", ["Update Existing Progress", "Add New Production Batch"])
        
        if update_type == "Add New Production Batch":
            with st.form("new_prod"):
                m_type = st.text_input("DRONE MODEL TYPE")
                m_time = st.text_input("ESTIMATED TIMELINE (e.g. 10 Days)")
                if st.form_submit_button("COMMENCE PRODUCTION"):
                    cursor.execute("INSERT INTO Manufacturing_Queue (drone_type, progress_percent, est_timeline) VALUES (?, 0, ?)", (m_type, m_time))
                    conn.commit()
                    st.success("New production batch initialized.")
        else:
            jobs = cursor.execute("SELECT job_id, drone_type FROM Manufacturing_Queue").fetchall()
            target_job = st.selectbox("SELECT BATCH", options=[j[0] for j in jobs], format_func=lambda x: dict(jobs)[x])
            new_prog = st.slider("SET PROGRESS %", 0, 100)
            if st.button("SYNC PROGRESS"):
                cursor.execute("UPDATE Manufacturing_Queue SET progress_percent=? WHERE job_id=?", (new_prog, target_job))
                conn.commit()
                st.rerun()

else:
    if mode == "OBSERVE & REPORT":
        st.subheader("📦 SPARE PARTS REPORT")
        inv = pd.read_sql_query("SELECT part_id as ID, part_name as Part, qty_available as [Stock], status FROM Inventory_Parts", conn)
        st.dataframe(inv, use_container_width=True, hide_index=True)
    else:
        st.subheader("🔧 SPARES STOCK UPDATE")
        update_type = st.selectbox("UPDATE TYPE", ["Add New Part Type", "Update Existing Part Quantity"])
        
        if update_type == "Add New Part Type":
            with st.form("new_part"):
                p_name = st.text_input("PART NAME")
                p_qty = st.number_input("INITIAL QTY", min_value=1)
                if st.form_submit_button("REGISTER COMPONENT"):
                    cursor.execute("INSERT INTO Inventory_Parts (part_name, qty_available, qty_demanded, status) VALUES (?,?,0,'Healthy')", (p_name, p_qty))
                    conn.commit()
                    st.success("New part registered in warehouse.")
        else:
            parts = cursor.execute("SELECT part_id, part_name FROM Inventory_Parts").fetchall()
            target_part = st.selectbox("SELECT PART BY ID/NAME", options=[p[0] for p in parts], format_func=lambda x: f"ID {x}: {dict(parts)[x]}")
            new_qty = st.number_input("QUANTITY RECEIVED", min_value=1)
            if st.button("UPDATE INVENTORY"):
                cursor.execute("UPDATE Inventory_Parts SET qty_available = qty_available + ? WHERE part_id=?", (new_qty, target_part))
                conn.commit()
                st.success("Stock quantity updated.")

conn.close()
