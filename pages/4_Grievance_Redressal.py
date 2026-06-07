# pages/4_Grievance_Redressal.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="DIMS - Grievances", layout="wide")

# --- UNIFIED DASHBOARD CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    .ticket-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px;
    }
    .badge-open { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;}
    .badge-closed { background-color: #dcfce3; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("🛡️ Grievance & Maintenance Ticketing")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Auto-create the Grievances table if it doesn't exist yet
cursor.execute('''CREATE TABLE IF NOT EXISTS Grievances (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submitter TEXT,
                    category TEXT,
                    hardware_sn TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'Open',
                    submission_date TEXT,
                    resolution_notes TEXT)''')
conn.commit()

current_role = st.session_state.get('role', 'User_Unit')
current_user = st.session_state.get('username', 'Unknown')

# --- WORKFLOW 1: ADMIN RESOLUTION DASHBOARD ---
if current_role == 'Admin':
    st.subheader("📋 Active Support Tickets")
    
    open_tickets = pd.read_sql_query("SELECT * FROM Grievances WHERE status='Open'", conn)
    
    if not open_tickets.empty:
        for idx, row in open_tickets.iterrows():
            st.markdown(f"<div class='ticket-card'>", unsafe_allow_html=True)
            st.markdown(f"<span class='badge-open'>OPEN TICKET #{row['ticket_id']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Reported by:** {row['submitter']} | **Category:** {row['category']} | **S/N:** {row['hardware_sn']}")
            st.markdown(f"**Issue Description:** {row['description']}")
            st.markdown(f"**Date:** {row['submission_date']}")
            
            with st.form(key=f"resolve_form_{row['ticket_id']}"):
                resolution = st.text_area("Admin Resolution Notes")
                if st.form_submit_button("Mark as Resolved & Close Ticket"):
                    cursor.execute("UPDATE Grievances SET status='Resolved', resolution_notes=? WHERE ticket_id=?", (resolution, row['ticket_id']))
                    conn.commit()
                    st.toast(f"Ticket #{row['ticket_id']} resolved successfully.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Excellent. No open grievances or maintenance tickets at this time.")
        
    st.divider()
    st.subheader("🗄️ Resolved Tickets Archive")
    closed_tickets = pd.read_sql_query("SELECT ticket_id AS [Ticket #], submitter AS [Unit], category AS [Category], hardware_sn AS [Serial], resolution_notes AS [Resolution] FROM Grievances WHERE status='Resolved'", conn)
    if not closed_tickets.empty:
        st.dataframe(closed_tickets, use_container_width=True, hide_index=True)

# --- WORKFLOW 2: USER SUBMISSION FORM ---
else:
    st.markdown("Submit maintenance alerts, damaged payload reports, or logistical delays directly to the Central Command dashboard.")
    
    with st.form("grievance_submission_form", clear_on_submit=True):
        st.markdown("<div class='ticket-card'>", unsafe_allow_html=True)
        g_cat = st.selectbox("Issue Category", ["Hardware Damage", "Software/Telemetry Failure", "Missing Parts", "Logistics Delay", "Other"])
        g_sn = st.text_input("Associated Hardware Serial Number (If applicable)", placeholder="e.g., SN-NV51-26-001")
        g_desc = st.text_area("Detailed Issue Description")
        
        if st.form_submit_button("Submit Grievance to Command", use_container_width=True):
            if g_desc:
                cursor.execute("""
                    INSERT INTO Grievances (submitter, category, hardware_sn, description, submission_date) 
                    VALUES (?, ?, ?, ?, ?)""", 
                    (current_user, g_cat, g_sn, g_desc, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("Your ticket has been securely transmitted to Logistics Command.")
            else:
                st.error("Please provide a detailed description of the issue.")
        st.markdown("</div>", unsafe_allow_html=True)

conn.close()
