import streamlit as st
import sqlite3
import db_setup

# Initialize DB on every boot to ensure schema is current
db_setup.init_db()

st.set_page_config(page_title="EME Drone Command", layout="wide", initial_sidebar_state="expanded")

# --- MILITARY TECH CSS INJECTION ---
st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Tactical Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid #00d4ff33;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
        border-right: 2px solid #00d4ff1a;
    }

    /* Military Buttons */
    .stButton>button {
        border: 1px solid #00d4ff !important;
        background-color: #1a1c24 !important;
        color: #00d4ff !important;
        border-radius: 0px !important;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff !important;
        color: #0e1117 !important;
        box-shadow: 0 0 15px #00d4ff;
    }

    /* Status Cards */
    .metric-card {
        background: #1a1c24;
        padding: 15px;
        border-left: 5px solid #00d4ff;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN / SESSION LOGIC ---
def verify_login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role, unit_id FROM Users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': None, 'unit_id': None, 'username': None})

if not st.session_state.logged_in:
    # EME Logo Placeholder - Replace with actual URL
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/EME_Crest.png/220px-EME_Crest.png", width=150)
    
    st.markdown("<h1 style='text-align: center;'>EME DRONE FACILITY PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>SECURE LOGISTICS & MANUFACTURING GATEWAY</p>", unsafe_allow_html=True)
    
    with st.container():
        _, login_col, _ = st.columns([1,2,1])
        with login_col:
            with st.form("login_form"):
                u = st.text_input("USER IDENTIFICATION")
                p = st.text_input("ACCESS KEY", type="password")
                if st.form_submit_button("AUTHORIZE ACCESS"):
                    user = verify_login(u, p)
                    if user:
                        st.session_state.update({'logged_in': True, 'user_id': user[0], 'role': user[1], 'unit_id': user[2], 'username': u})
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID CREDENTIALS")

else:
    # --- HOMEPAGE TILES ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/EME_Crest.png/220px-EME_Crest.png", width=80)
    st.sidebar.title("COMMANDER'S HUD")
    st.sidebar.info(f"OPERATOR: {st.session_state.username}\n\nROLE: {st.session_state.role}")
    
    if st.sidebar.button("TERMINATE SESSION"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown(f"<h1>FACILITY OVERVIEW: {st.session_state.role}</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("<div class='metric-card'><h3>📘 BROCHURE</h3><p>Technical specifications and platform schematics.</p></div>", unsafe_allow_html=True)
        st.page_link("pages/1_Info_Brochure.py", label="ENTER MODULE", icon="📡")
    with t2:
        st.markdown("<div class='metric-card'><h3>📦 DISTRIBUTION</h3><p>Asset tracking and unit-level deployment logs.</p></div>", unsafe_allow_html=True)
        st.page_link("pages/2_Distribution.py", label="ENTER MODULE", icon="🚛")
    with t3:
        st.markdown("<div class='metric-card'><h3>⚙️ INVENTORY</h3><p>Manufacturing queue and spare parts logistics.</p></div>", unsafe_allow_html=True)
        st.page_link("pages/3_Inventory.py", label="ENTER MODULE", icon="🛠️")
