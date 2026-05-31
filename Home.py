import streamlit as st
import sqlite3
import db_setup
import os

db_setup.init_db()

st.set_page_config(page_title="EME Drone Command", layout="wide", initial_sidebar_state="expanded")

# Inject Tactical Consolidated Layout
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1a1c24 !important; border-right: 2px solid #00d4ff1a; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; }
    
    /* Interactive Card Modules functioning as Direct Page Anchors */
    .tile-container {
        background: #1a1c24;
        padding: 24px;
        border-left: 5px solid #00d4ff;
        border-radius: 4px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 15px;
    }
    .tile-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("eme_logo.png"):
        st.image("eme_logo.png", width=150)
    else:
        st.info("📌 Upload 'eme_logo.png' to GitHub root directory to show crest.")
        
    if st.session_state.get('logged_in'):
        st.page_link("Home.py", label="🏠 RETURN TO HQ UNIT", use_container_width=True)
        st.divider()
        st.markdown(f"**SECURE USER:** {st.session_state.username}")
        st.markdown(f"**ROLE SECURE INDEX:** {st.session_state.role}")
        if st.button("TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

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
    st.markdown("<h1 style='text-align: center;'>EME DRONE LOGISTICS ARCHITECTURE</h1>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1,2,1])
    with login_col:
        with st.form("login_gate"):
            u = st.text_input("ENTER CREDENTIAL ASSIGNMENT")
            p = st.text_input("SECURE ACCESS KEY", type="password")
            if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                user = verify_login(u, p)
                if user:
                    st.session_state.update({'logged_in': True, 'user_id': user[0], 'role': user[1], 'unit_id': user[2], 'username': u})
                    st.rerun()
                else:
                    st.error("ACCESS MUTED: AUTHENTICATION BREACH")
else:
    st.markdown(f"<h1>TACTICAL RECONNAISSANCE COMMAND CONSOLE</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.columns(3)
    
    with t1:
        if st.button("📡 OPEN TECHNICAL PORTFOLIO", use_container_width=True):
            st.switch_page("pages/1_Info_Brochure.py")
        st.markdown("<div class='tile-container'><h3>📘 BROCHURE</h3><p>Central engineering library containing detailed system schematics.</p></div>", unsafe_allow_html=True)
        
    with t2:
        if st.button("🚛 OPEN LOGISTICS RADAR", use_container_width=True):
            st.switch_page("pages/2_Distribution.py")
        st.markdown("<div class='tile-container'><h3>📦 DISTRIBUTION</h3><p>Granular distribution mapping across forward operating formations.</p></div>", unsafe_allow_html=True)
        
    with t3:
        if st.button("🛠️ OPEN WAREHOUSE CONSOLE", use_container_width=True):
            st.switch_page("pages/3_Inventory.py")
        st.markdown("<div class='tile-container'><h3>⚙️ INVENTORY</h3><p>Production line trackers and spare component asset reserves.</p></div>", unsafe_allow_html=True)
