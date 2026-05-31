import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Drone Info Brochure", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied. Please log in on the Home page first.")
    st.stop()

st.title("📘 Drone Information Brochure")
role = st.session_state.role

# --- Handle Manufacturer Write Privileges ---
if role == 'Manufacturer':
    st.subheader("🛠️ Add New Drone Specification")
    with st.form("add_drone_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Drone Model Name")
            m_role = st.text_input("Operational Role (e.g., Surveillance)")
            m_flight = st.text_input("Flight Endurance (e.g., 60 Mins)")
        with col2:
            m_payload = st.text_input("Max Payload Capacity")
            m_specs = st.text_area("Technical Specifications & Data")
        
        submit = st.form_submit_button("Publish to Catalog")
        if submit:
            if m_name and m_role:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) VALUES (?,?,?,?,?)", 
                                   (m_name, m_role, m_flight, m_payload, m_specs))
                    conn.commit()
                    st.success(f"Successfully added '{m_name}' to the technical database!")
                except sqlite3.IntegrityError:
                    st.error("A drone model with this name already exists.")
                conn.close()
            else:
                st.error("Model Name and Role are required fields.")

st.divider()
st.subheader("📋 Active Manufacturing & Technical Portfolio")

# --- Fetch and Display Brochure Data (All Roles can read) ---
conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT model_name AS [Model Name], role_type AS [Role], flight_time AS [Flight Time], payload_capacity AS [Payload], technical_specs AS [Technical Specs] FROM Drone_Models", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No drone specifications found in the database.")
