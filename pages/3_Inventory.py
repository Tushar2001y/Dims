import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Factory & Inventory", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2 { color: #00d4ff !important; }
    .stProgress > div > div > div > div { background-color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or st.session_state.role == 'User_Unit':
    st.error("🚫 RESTRICTED ACCESS: LOGISTICS COMMAND ONLY")
    st.stop()

st.title("🛠️ MANUFACTURING & SPARES COMMAND")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# --- MANUFACTURING QUEUE ---
st.subheader("🏭 ACTIVE PRODUCTION LINES")
mq = pd.read_sql_query("SELECT * FROM Manufacturing_Queue", conn)
for _, row in mq.iterrows():
    col1, col2 = st.columns([1, 4])
    col1.write(f"**{row['drone_type']}**")
    col2.progress(row['progress_percent'], text=f"COMPLETION: {row['progress_percent']}% | EST: {row['est_timeline']}")

if st.session_state.role == 'Manufacturer':
    with st.expander("🔧 ADJUST PRODUCTION PARAMETERS"):
        job_id = st.selectbox("BATCH ID", mq['job_id'].tolist())
        new_val = st.slider("SET PROGRESS", 0, 100)
        if st.button("UPDATE LINE"):
            cursor.execute("UPDATE Manufacturing_Queue SET progress_percent=? WHERE job_id=?", (new_val, job_id))
            conn.commit()
            st.rerun()

st.divider()

# --- INVENTORY ---
st.subheader("📦 COMPONENT STOCK LEVELS")
inv = pd.read_sql_query("SELECT part_name, qty_available, qty_demanded, status FROM Inventory_Parts", conn)
st.dataframe(inv, use_container_width=True, hide_index=True)

conn.close()
