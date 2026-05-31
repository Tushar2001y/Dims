import streamlit as st
import sqlite3
import os

# --- DATABASE AUTO-FIX ---
def check_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Ensure Receipt_Requests exists to fix the red error
    cursor.execute('''CREATE TABLE IF NOT EXISTS Receipt_Requests (
                        receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name TEXT, serial_number TEXT, unit_id INTEGER,
                        arrival_date TEXT, letter_number TEXT, status TEXT)''')
    # Ensure images column exists in Drone_Models if not already there
    try:
        cursor.execute("ALTER TABLE Drone_Models ADD COLUMN image_path TEXT")
    except:
        pass 
    conn.commit()
    conn.close()

check_db()

st.set_page_config(page_title="EME Drone Command", layout="wide")

# Tactical CSS for clickable tiles
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1a1c24 !important; }
    .nav-card {
        background: #1a1c24;
        padding: 30px;
        border-left: 5px solid #00d4ff;
        border-radius: 4px;
        text-align: center;
        transition: 0.3s;
    }
    .nav-card:hover { border-left: 10px solid #00d4ff; background: #252932; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with Logo
with st.sidebar:
    if os.path.exists("eme_logo.png"):
        st.image("eme_logo.png", width=150)
    if st.session_state.get('logged_in'):
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

# Login / Dashboard Logic
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    # ... (Keep your existing Login Form here) ...
    if st.button("SECURE LOGIN (MOCK)"): # Placeholder for your actual login logic
        st.session_state.update({'logged_in': True, 'role': 'Manufacturer', 'username': 'admin', 'unit_id': 1})
        st.rerun()
else:
    st.title("TACTICAL COMMAND DASHBOARD")
    cols = st.columns(3)
    
    pages = [
        {"title": "BROCHURE", "desc": "Technical Specs & STL Models", "icon": "📡", "path": "pages/1_Info_Brochure.py"},
        {"title": "DISTRIBUTION", "desc": "Fleet Logs & Unit Receipts", "icon": "🚛", "path": "pages/2_Distribution.py"},
        {"title": "INVENTORY", "desc": "Production & Spares", "icon": "🛠️", "path": "pages/3_Inventory.py"}
    ]

    for i, p in enumerate(pages):
        with cols[i]:
            st.markdown(f"<div class='nav-card'><h2>{p['icon']} {p['title']}</h2><p>{p['desc']}</p></div>", unsafe_allow_html=True)
            if st.button(f"ENTER {p['title']} MODULE", key=f"nav_{i}", use_container_width=True):
                st.switch_page(p['path'])
