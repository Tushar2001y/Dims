import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import db_setup

# --- 1. INITIALIZATION & CONFIGURATION ---
# This ensures the database is built once upon server boot
@st.cache_resource
def initialize_database():
    db_setup.init_db()
    return True

initialize_database()

st.set_page_config(page_title="DIMS - Dashboard Console", layout="wide", initial_sidebar_state="expanded")

# --- 2. GLOBAL STYLESHEET ---
st.markdown("""
    <style>
    /* Force Light Theme */
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    h1, h2, h3, h4 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    
    /* Hide Streamlit Native Sidebar Navigation to prevent duplicates */
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 36px; font-weight: 700; color: #2563eb; line-height: 1.2; }
    .metric-label { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION MANAGEMENT & LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>📦 D-dims Access Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Operator ID")
            password = st.text_input("Passcode", type="password")
            submit = st.form_submit_button("Authenticate Session", use_container_width=True, type="primary")
            
            if submit:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("SELECT user_id, role, node_id FROM Users WHERE username=? AND password=?", (username, password))
                user = c.fetchone()
                conn.close()
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['role'] = user[1]
                    st.session_state['node_id'] = user[2]
                    st.rerun()
                else:
                    st.error("Invalid credentials. Connection refused.")
    st.stop()

# --- 4. SECURE SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-top:0; margin-bottom:24px;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
    st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
    st.page_link("pages/2_Distribution.py", label="🚛 Fleet Deployment", use_container_width=True)
    st.page_link("pages/3_Inventory.py", label="🛠️ Inventory & Assembly", use_container_width=True)
    st.page_link("pages/5_AI_Assistant.py", label="🤖 AI Assistant", use_container_width=True)
    
    st.divider()
    st.markdown(f"<p style='font-size:13px; color:#64748b; margin-bottom:4px;'>User Profile:</p><strong style='color:#0f172a;'>{st.session_state.username} ({st.session_state.role})</strong>", unsafe_allow_html=True)
    
    if st.button("Log Out Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 5. DASHBOARD METRICS CALCULATION ---
st.title("Dashboard Overview")
st.markdown("<p style='color: #64748b; margin-top: -10px; margin-bottom: 24px;'>Live telemetry and logistical status tracking.</p>", unsafe_allow_html=True)

conn = sqlite3.connect('database.db')

# Metric 1: Total Active Fleet
active_fleet_count = pd.read_sql_query("SELECT COUNT(*) as count FROM Distributed_Assets WHERE status != 'BER'", conn).iloc[0]['count']

# Metric 2: Pending Maker-Checker Indents
pending_indents_count = pd.read_sql_query("SELECT COUNT(*) as count FROM FleetRequests WHERE status != 'Approved'", conn).iloc[0]['count']

# Metric 3: Spares Health
spares_df = pd.read_sql_query("SELECT status FROM Spares_Inventory", conn)
if not spares_df.empty:
    healthy_spares = len(spares_df[spares_df['status'] == 'Healthy'])
    readiness_pct = (healthy_spares / len(spares_df)) * 100
else:
    readiness_pct = 0.0

# Render Top KPIs
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Active Fleet</div><div class='metric-value'>{active_fleet_count}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Pending Indent Requests</div><div class='metric-value'>{pending_indents_count}</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Supply Chain Health</div><div class='metric-value'>{readiness_pct:.1f}%</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. PLOTLY VISUALIZATIONS ---
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Active Fleet Distribution")
    fleet_df = pd.read_sql_query("SELECT model_name, COUNT(*) as count FROM Distributed_Assets GROUP BY model_name", conn)
    if not fleet_df.empty:
        fig_fleet = px.pie(fleet_df, values='count', names='model_name', hole=0.4, 
                           color_discrete_sequence=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd'])
        fig_fleet.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_fleet, use_container_width=True)
    else:
        st.info("No active fleet telemetry available.")

with c2:
    st.markdown("### Indents by Status Pipeline")
    pipeline_df = pd.read_sql_query("SELECT status, COUNT(*) as count FROM FleetRequests GROUP BY status", conn)
    if not pipeline_df.empty:
        fig_pipeline = px.bar(pipeline_df, x='status', y='count', color='status',
                              color_discrete_map={'Pending': '#f59e0b', 'Pending_GSEM': '#3b82f6', 'Approved': '#10b981'})
        fig_pipeline.update_layout(margin=dict(t=20, b=20, l=20, r=20), xaxis_title="", yaxis_title="Number of Indents", showlegend=False)
        st.plotly_chart(fig_pipeline, use_container_width=True)
    else:
        st.info("No Maker-Checker indents registered.")

conn.close()
