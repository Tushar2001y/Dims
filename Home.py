import streamlit as st
import sqlite3

import db_setup
db_setup.init_db()

st.set_page_config(page_title="Global Drone Portal", layout="centered")

# --- Database Connection ---
def verify_login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, role, unit_id FROM Users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.unit_id = None
    st.session_state.username = None

# --- Login UI ---
if not st.session_state.logged_in:
    st.title("Secure Access Portal")
    st.markdown("Please log in with your assigned credentials.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Authenticate")
        
        if submit:
            user = verify_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.role = user[1]
                st.session_state.unit_id = user[2]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")

# --- Logged-In State (The Router) ---
else:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.replace('_', ' ')}")
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.unit_id = None
        st.rerun()

    st.title(f"Welcome, {st.session_state.username}")
    
    if st.session_state.role == 'Manufacturer':
        st.success("Admin Access Granted: You have full read/write privileges.")
    elif st.session_state.role == 'User_Unit':
        st.info("Operator Access Granted: Viewing data restricted to your specific unit.")
    elif st.session_state.role == 'Corps_Commander':
        st.warning("Executive Access Granted: Global read-only and approval workflows active.")
        
    st.markdown("### Please select a module from the sidebar to continue.")
