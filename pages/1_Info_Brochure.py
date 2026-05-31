import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Technical Dossier", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ AUTHENTICATION REQUIRED")
    st.stop()

st.title("📡 Drone Technical Dossier")

if st.session_state.role == 'Manufacturer':
    with st.expander("➕ REGISTER NEW PLATFORM SPECIFICATIONS"):
        with st.form("add_drone"):
            c1, c2 = st.columns(2)
            m_name = c1.text_input("PLATFORM NAME")
            m_role = c1.text_input("DESIGNATED ROLE")
            m_flight = c2.text_input("MAX ENDURANCE")
            m_payload = c2.text_input("PAYLOAD CAPACITY")
            m_specs = st.text_area("DETAILED SCHEMATIC DATA")
            if st.form_submit_button("UPLOAD TO COMMAND DATABASE"):
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) VALUES (?,?,?,?,?)", (m_name, m_role, m_flight, m_payload, m_specs))
                conn.commit()
                conn.close()
                st.toast("DATA SYNCHRONIZED")
                st.rerun()

st.subheader("CURRENT FLEET SPECIFICATIONS")
conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT model_name as Platform, role_type as Role, flight_time as Endurance, payload_capacity as Payload, technical_specs as [Tech Specs] FROM Drone_Models", conn)
conn.close()

st.dataframe(df, use_container_width=True, hide_index=True)
