import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Distribution", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.stop()

st.title("🚛 ASSET DISTRIBUTION LOGS")
conn = sqlite3.connect('database.db')

if st.session_state.role in ['Manufacturer', 'Corps_Commander']:
    st.subheader("🔍 FLEET SEARCH & FILTER")
    c1, c2 = st.columns(2)
    units = pd.read_sql_query("SELECT unit_name FROM Units WHERE unit_id != 1", conn)['unit_name'].tolist()
    models = pd.read_sql_query("SELECT model_name FROM Drone_Models", conn)['model_name'].tolist()
    
    sel_unit = c1.multiselect("FILTER BY UNIT", ["ALL"] + units, default="ALL")
    sel_model = c2.multiselect("FILTER BY MODEL", ["ALL"] + models, default="ALL")

    query = "SELECT d.serial_number, d.model_name, u.unit_name, d.status FROM Distributed_Assets d JOIN Units u ON d.assigned_unit_id = u.unit_id"
    df = pd.read_sql_query(query, conn)
    
    if "ALL" not in sel_unit: df = df[df['unit_name'].isin(sel_unit)]
    if "ALL" not in sel_model: df = df[df['model_name'].isin(sel_model)]
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.subheader("📊 DISTRIBUTION SUMMARY")
    st.table(df.groupby(['unit_name', 'model_name']).size().reset_index(name='Quantity'))

conn.close()
