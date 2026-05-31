import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Distribution", layout="wide")

# (Inject CSS here same as Home.py for sidebar consistency)

st.title("🚛 DETAILED DISTRIBUTION LOGS")
conn = sqlite3.connect('database.db')

if st.session_state.role in ['Manufacturer', 'Corps_Commander']:
    st.subheader("🔍 GLOBAL SEARCH & FILTER")
    col1, col2 = st.columns(2)
    
    with col1:
        units = pd.read_sql_query("SELECT unit_name FROM Units WHERE unit_id != 1", conn)['unit_name'].tolist()
        sel_unit = st.multiselect("FILTER BY FORMATION", ["ALL"] + units, default="ALL")
    
    with col2:
        models = pd.read_sql_query("SELECT model_name FROM Drone_Models", conn)['model_name'].tolist()
        sel_model = st.multiselect("FILTER BY DRONE TYPE", ["ALL"] + models, default="ALL")

    query = "SELECT d.serial_number, d.model_name, u.unit_name, u.command_theater, d.status FROM Distributed_Assets d JOIN Units u ON d.assigned_unit_id = u.unit_id"
    df = pd.read_sql_query(query, conn)
    
    if "ALL" not in sel_unit: df = df[df['unit_name'].isin(sel_unit)]
    if "ALL" not in sel_model: df = df[df['model_name'].isin(sel_model)]
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Summary Table
    st.subheader("📈 QUANTITY BY FORMATION")
    summary = df.groupby(['unit_name', 'model_name']).size().reset_index(name='Quantity')
    st.table(summary)

conn.close()
