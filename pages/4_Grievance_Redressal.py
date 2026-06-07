# pages/4_Grievance_Redressal.py
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="DIMS Grievance Desk", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ ACCESS DENIED")
    st.stop()

st.title("🛠️ COMPONENT DEFECT & GRIEVANCE REDRESSAL DESK")

# --- EXPERT AI DIAGNOSTIC ENGINE (DETERMINISTIC LLM LAYER) ---
def query_tactical_llm(subject, description):
    context_pool = {
        "telemetry": "⚡ SYSTEM DIAGNOSTIC ANALYSIS: Detected compass variance calibration error. RECOMMENDATION: Re-run IMU stabilization sequence on clean horizontal orientation vector away from structural iron blocks before flight.",
        "payload": "📦 SYSTEM DIAGNOSTIC ANALYSIS: Current drop clamp interface reports mechanical power resistance. RECOMMENDATION: Clean locking pins with chemical cleaner and cross-verify physical latch continuity.",
        "5g": "📡 SYSTEM DIAGNOSTIC ANALYSIS: 5G Handshake latency exceeding limits. RECOMMENDATION: Verify active network SIM binding profiles and inspect condition of local high-gain receiver components."
    }
    for trigger, resolution in context_pool.items():
        if trigger in subject.lower() or trigger in description.lower():
            return resolution
    return "⚙️ ANALYSIS COMPLETION: Issue registered safely inside the system logs. Diagnostic criteria indeterminate. System is routing issue details to Manufacturer Admin queue for technical resolution."

# --- TICKET SUBMISSION GATEWAY ---
with st.form("grievance_submission", clear_on_submit=True):
    st.subheader("📬 LOG NEW TACTICAL SYSTEM DEFECT SUMMARY")
    sub = st.text_input("FAULT SYSTEM SUBJECT MATTER (e.g., 5G Transceiver Latency)")
    desc = st.text_area("DETAILED ANOMALY LOG DESCRIPTION")
    
    if st.form_submit_button("INITIALIZE RENDER FOR CELL REVIEW"):
        if sub and desc:
            ai_verdict = query_tactical_llm(sub, desc)
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Grievances (user_id, username, node_id, subject, description, ai_resolution_summary) 
                              VALUES (?, ?, ?, ?, ?, ?)""", 
                           (st.session_state.node_id, st.session_state.username, st.session_state.node_id, sub, desc, ai_verdict))
            conn.commit()
            conn.close()
            
            st.subheader("🤖 AUTOMATED ASSISTANT RESOLUTION FEEDBACK")
            st.info(ai_verdict)
        else:
            st.error("Ensure both input fault fields are fully declared.")

st.divider()

# --- HISTORICAL LEDGER DISCOVERY ---
st.subheader("📋 TICKET REPOSITORY RECORDS")
conn = sqlite3.connect('database.db')

if st.session_state.role == 'Admin':
    # Admins inspect all technical grievances across the enterprise
    ledger_df = pd.read_sql_query("SELECT ticket_id, username, subject, description, ai_resolution_summary, status FROM Grievances", conn)
else:
    # Subordinate units can track only their own filed tickers
    ledger_df = pd.read_sql_query("SELECT ticket_id, subject, description, ai_resolution_summary, status FROM Grievances WHERE user_id=?", conn, params=(st.session_state.node_id,))

if not ledger_df.empty:
    st.dataframe(ledger_df, use_container_width=True, hide_index=True)
else:
    st.success("Log record matrix clear: No anomalies logged across current operational sectors.")
conn.close()
