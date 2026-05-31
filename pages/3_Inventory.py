import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventory Control", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2, h3 { color: #00d4ff !important; }</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or st.session_state.role == 'User_Unit':
    st.error("🛑 RESTRICTED MODULAR NODE: LOGISTICS ASSIGNMENT CHANNELS ONLY")
    st.stop()

st.title("⚙️ FACTORY INVENTORY & WAREHOUSE CONSOLE")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# STEP 1: Select Category
category = st.radio("SELECT OPERATIONAL CATEGORY", ["PRODUCTION LINE TRACKER", "SPARES WAREHOUSE LOGISTICS"], horizontal=True)
st.divider()

# STEP 2: Enforce Read-Only Access Restrictions for the Commander
if st.session_state.role == 'Corps_Commander':
    st.warning("👁️ READ-ONLY ACCESS ENABLED FOR HIGHER HQ")
    mode = "OBSERVE & REPORT"
else:
    mode = st.radio("SELECT CONTROL FUNCTION", ["OBSERVE & REPORT", "UPDATE RECORDS"], horizontal=True)

# --- PRODUCTION LINE PROCESSING BLOCK ---
if category == "PRODUCTION LINE TRACKER":
    if mode == "OBSERVE & REPORT":
        st.subheader("🏭 ASSEMBLY telemetry")
        mq = pd.read_sql_query("SELECT drone_type as [Batch Designation], progress_percent as [Build Index %], est_timeline as [Remaining Window] FROM Manufacturing_Queue", conn)
        for _, row in mq.iterrows():
            st.write(f"**{row['Batch Designation']}** | Delivery Target: {row['Remaining Window']}")
            st.progress(int(row['Build Index %']))
    else:
        st.subheader("⚙️ MODIFY ASSEMBLIES")
        update_type = st.selectbox("SELECT STEP ACTION", ["Update Existing Progress", "Add New Production Batch"])
        
        if update_type == "Add New Production Batch":
            with st.form("new_batch"):
                m_type = st.text_input("DRONE TYPE ARCHITECTURE")
                m_time = st.text_input("TARGET TIMELINE WINDOW (e.g. 14 Days)")
                if st.form_submit_button("COMMENCE ASSEMBLY LINE"):
                    if m_type and m_time:
                        cursor.execute("INSERT INTO Manufacturing_Queue (drone_type, progress_percent, est_timeline) VALUES (?, 0, ?)", (m_type, m_time))
                        conn.commit()
                        st.success("New production run initialized.")
                        st.rerun()
        else:
            jobs = cursor.execute("SELECT job_id, drone_type FROM Manufacturing_Queue").fetchall()
            if jobs:
                t_job = st.selectbox("CHOOSE ASSEMBLY BATCH ID", options=[j[0] for j in jobs], format_func=lambda x: dict(jobs)[x])
                n_prog = st.slider("CALIBRATE PRODUCTION INDEX", 0, 100)
                if st.button("COMMIT TELEMETRY CHANGES"):
                    cursor.execute("UPDATE Manufacturing_Queue SET progress_percent=? WHERE job_id=?", (n_prog, t_job))
                    conn.commit()
                    st.rerun()

# --- SPARES LOGISTICS PROCESSING BLOCK ---
else:
    if mode == "OBSERVE & REPORT":
        st.subheader("📦 STOCK ROOM BALANCES")
        inv = pd.read_sql_query("SELECT part_id as [Spare Part ID], part_name as [Component Name], qty_available as [Quantity in Warehouse], status as [Health Index] FROM Inventory_Parts", conn)
        st.dataframe(inv, use_container_width=True, hide_index=True)
    else:
        st.subheader("🔧 RE-CALIBRATE SPARE STOCKS")
        update_type = st.selectbox("SELECT UPDATE SUB-VIEW", ["Add Completely New Spare Component Type", "Receive Quantity For Existing Spare ID"])
        
        if update_type == "Add Completely New Spare Component Type":
            with st.form("new_spare_type"):
                p_name = st.text_input("COMPONENT PARTER NAME / NOMENCLATURE")
                p_qty = st.number_input("RECEIVING STOCK QUANTITY", min_value=1, step=1)
                if st.form_submit_button("REGISTER IN DATABASE"):
                    if p_name:
                        cursor.execute("INSERT INTO Inventory_Parts (part_name, qty_available, qty_demanded, status) VALUES (?,?,0,'Healthy')", (p_name, p_qty))
                        conn.commit()
                        st.success("Component successfully listed in asset registers.")
                        st.rerun()
        else:
            parts = cursor.execute("SELECT part_id, part_name FROM Inventory_Parts").fetchall()
            if parts:
                t_part = st.selectbox("CHOOSE SPARE ID RECIPIENT", options=[p[0] for p in parts], format_func=lambda x: f"ID {x} -> {dict(parts)[x]}")
                add_qty = st.number_input("INBOUND QUANTITY", min_value=1, step=1)
                if st.button("INCREMENT LOGISTICS BALANCE"):
                    cursor.execute("UPDATE Inventory_Parts SET qty_available = qty_available + ? WHERE part_id=?", (add_qty, t_part))
                    conn.commit()
                    st.success("Inventory stock levels incremented and updated.")
                    st.rerun()

conn.close()
