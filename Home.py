import streamlit as st
import sqlite3
import db_setup
import os

db_setup.init_db()

st.set_page_config(page_title="EME Drone Command", layout="wide", initial_sidebar_state="expanded")

# --- UNIFIED TACTICAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1a1c24 !important; border-right: 2px solid #00d4ff1a; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { border: 1px solid #00d4ff !important; background-color: #1a1c24 !important; color: #00d4ff !important; border-radius: 0px !important; }
    .stButton>button:hover { background-color: #00d4ff !important; color: #0e1117 !important; box-shadow: 0 0 15px #00d4ff; }
    .metric-card { background: #1a1c24; padding: 15px; border-left: 5px solid #00d4ff; border-radius: 4px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR LOGO & NAVIGATION ---
with st.sidebar:
    if os.path.exists("eme_logo.png"):
        st.image("eme_logo.png", width=150)
    else:
        st.info("Upload eme_logo.png to GitHub")
    
    if st.session_state.get('logged_in'):
        st.page_link("Home.py", label="🏠 RETURN TO HQ", use_container_width=True)
        st.divider()
        st.markdown(f"**OPERATOR:** {st.session_state.username}")
        st.markdown(f"**CORPS:** EME | {st.session_state.role}")
        if st.button("TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

# --- LOGIN LOGIC ---
def verify_login(u, p):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role, unit_id FROM Users WHERE username=? AND password=?", (u, p))
    user = cursor.fetchone()
    conn.close()
    return user

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': None, 'unit_id': None, 'username': None})

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>EME DRONE FACILITY PORTAL</h1>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1,2,1])
    with login_col:
        with st.form("login"):
            u = st.text_input("USER ID")
            p = st.text_input("ACCESS KEY", type="password")
            if st.form_submit_button("AUTHORIZE"):
                user = verify_login(u, p)
                if user:
                    st.session_state.update({'logged_in': True, 'user_id': user[0], 'role': user[1], 'unit_id': user[2], 'username': u})
                    st.rerun()
                else: st.error("INVALID CREDENTIALS")
else:
    st.markdown(f"<h1>FACILITY OVERVIEW: {st.session_state.role}</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("<div class='metric-card'><h3>📘 BROCHURE</h3><p>Technical Specs</p></div>", unsafe_allow_html=True)
        st.page_link("pages/1_Info_Brochure.py", label="VIEW BROCHURE", icon="📡")
    with t2:
        st.markdown("<div class='metric-card'><h3>📦 DISTRIBUTION</h3><p>Unit Asset Logs</p></div>", unsafe_allow_html=True)
        st.page_link("pages/2_Distribution.py", label="VIEW DISTRIBUTION", icon="🚛")
    with t3:
        st.markdown("<div class='metric-card'><h3>⚙️ INVENTORY</h3><p>Production & Spares</p></div>", unsafe_allow_html=True)
        st.page_link("pages/3_Inventory.py", label="VIEW INVENTORY", icon="🛠️")
