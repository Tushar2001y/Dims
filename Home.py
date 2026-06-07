# Home.py
import streamlit as st
import sqlite3
import db_setup

db_setup.init_db()

st.set_page_config(page_title="DIMS - Dashboard", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Dashboard Stylesheet mirroring the target sample layout
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp { background-color: #f8fafc; color: #0f172a; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    
    /* Clean, Modern Typography */
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    
    /* Style Custom Info Cards */
    .dashboard-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .card-title { color: #64748b; font-size: 14px; text-transform: uppercase; font-weight: 500; }
    .card-value { color: #0f172a; font-size: 28px; font-weight: 700; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': None, 'node_id': None, 'username': None})

with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-top:0; margin-bottom:24px;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
        st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
        st.page_link("pages/2_Distribution.py", label="🚛 Fleet Deployment", use_container_width=True)
        st.page_link("pages/3_Inventory.py", label="🛠️ Inventory & Assembly", use_container_width=True)
        st.divider()
        st.markdown(f"<p style='font-size:13px; color:#64748b; margin-bottom:0;'>User Profile:</p><strong style='color:#0f172a;'>{st.session_state.username} ({st.session_state.role})</strong>", unsafe_allow_html=True)
        if st.button("Log Out Session", use_container_width=True):
            st.session_state.update({'logged_in': False, 'role': None, 'node_id': None, 'username': None})
            st.rerun()

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 40px;'>Sign in to DIMS</h1>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1.2, 1.5, 1.2])
    with login_col:
        with st.form("dims_login_gate"):
            u = st.text_input("Username / Command Assignment")
            p = st.text_input("Secure Access Key", type="password")
            if st.form_submit_button("Validate Credentials", use_container_width=True):
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, role, node_id FROM Users WHERE username=? AND password=?", (u, p))
                res = cursor.fetchone()
                conn.close()
                if res:
                    st.session_state.update({'logged_in': True, 'role': res[1], 'node_id': res[2], 'username': u})
                    st.rerun()
                else:
                    st.error("Authentication breach: Invalid credentials.")
else:
    st.markdown("<h1>Dashboard Overview</h1>", unsafe_allow_html=True)
    
    # Clean Metric Layout Rows matching target sample look
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='dashboard-card'><div class='card-title'>Total Active Fleet</div><div class='card-value'>389 Units</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='dashboard-card'><div class='card-title'>Pending Inbound Requests</div><div class='card-value'>12 Indents</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='dashboard-card'><div class='card-title'>System Operational Readiness</div><div class='card-value'>98.4%</div></div>", unsafe_allow_html=True)
        
    st.info("💡 Welcome to DIMS. Use the sidebar navigation console to monitor technical dossiers, adjust inventory stocks, or authorize field distributions across the 9 Corps operational zone.")
