import streamlit as st
import sqlite3
import pandas as pd
from graphviz import Digraph

st.set_page_config(page_title="DIMS - Fleet Deployment", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    .management-block { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 24px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("🚛 Fleet Deployment & Logistics Control")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

current_node_id = st.session_state.get('node_id', 1)
current_role = st.session_state.get('role', 'User_Unit')

def get_authorized_node_ids(user_node_id, role):
    if role in ['Admin', 'Commander']:
        res = cursor.execute("SELECT node_id FROM Org_Structure").fetchall()
        return [r[0] for r in res]
    
    user_node_id = int(user_node_id)
    all_nodes = cursor.execute("SELECT node_id, parent_id FROM Org_Structure").fetchall()
    
    tree_map = {}
    for n_id, p_id in all_nodes:
        if p_id is not None:
            tree_map.setdefault(int(p_id), []).append(int(n_id))
            
    authorized_ids = [user_node_id]
    queue = [user_node_id]
    while queue:
        current = queue.pop(0)
        if current in tree_map:
            for child in tree_map[current]:
                if child not in authorized_ids:
                    authorized_ids.append(child)
                    queue.append(child)
    return authorized_ids

auth_nodes = get_authorized_node_ids(current_node_id, current_role)
placeholders = ",".join("?" for _ in auth_nodes)

# --- WORKFLOW 1: TIER 1 ADMIN VERIFICATION ---
if current_role == 'Admin':
    st.subheader("📥 Tier 1: Pending Inbound Receipts")
    pending_df = pd.read_sql_query("SELECT r.*, o.node_name FROM Receipt_Requests r JOIN Org_Structure o ON r.unit_id = o.node_id WHERE r.status = 'Pending Verification'", conn)
    for idx, row in pending_df.iterrows():
        st.markdown("<div class='management-block'>", unsafe_allow_html=True)
        st.write(f"**Formation:** {row['node_name']} | **Model:** {row['model_name']} | **S/N:** {row['serial_number']}")
        c1, c2, _ = st.columns([2, 2, 6])
        if c1.button("Forward to Col GSEM", key=f"fwd_{idx}"):
            cursor.execute("UPDATE Receipt_Requests SET status='Pending_GSEM' WHERE receipt_id=?", (row['receipt_id'],))
            conn.commit()
            st.rerun()
        if c2.button("Reject", key=f"rej_{idx}"):
            cursor.execute("UPDATE Receipt_Requests SET status='Rejected' WHERE receipt_id=?", (row['receipt_id'],))
            conn.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- WORKFLOW 1.5: TIER 2 COMMANDER FINAL SANCTION ---
elif current_role == 'Commander':
    st.subheader("🛑 Tier 2: Final Command Sanction")
    gsem_df = pd.read_sql_query("SELECT r.*, o.node_name FROM Receipt_Requests r JOIN Org_Structure o ON r.unit_id = o.node_id WHERE r.status = 'Pending_GSEM'", conn)
    for idx, row in gsem_df.iterrows():
        st.markdown("<div class='management-block'>", unsafe_allow_html=True)
        st.write(f"**Formation:** {row['node_name']} | **Model:** {row['model_name']} | **S/N:** {row['serial_number']}")
        if st.button("Grant Final Sanction", key=f"app_{idx}"):
            cursor.execute("INSERT INTO Distributed_Assets (model_name, serial_number, assigned_unit_id, status, issue_date, auth_letter) VALUES (?, ?, (SELECT node_id FROM Org_Structure WHERE node_name=?), 'Operational', ?, ?)", 
                           (row['model_name'], row['serial_number'], row['node_name'], row['arrival_date'], row['letter_number']))
            cursor.execute("UPDATE Receipt_Requests SET status='Approved' WHERE receipt_id=?", (row['receipt_id'],))
            conn.commit()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- WORKFLOW 2: AGGREGATED DOSSIER & FLOWCHART ---
st.divider()
st.subheader("📋 Command Asset Overview")
mode = st.radio("View:", ["Summary Table", "Command Flow Chart"], horizontal=True)

if mode == "Summary Table":
    df = pd.read_sql_query(f"SELECT o.node_name as Formation, d.model_name, d.serial_number, d.status FROM Distributed_Assets d JOIN Org_Structure o ON d.assigned_unit_id = o.node_id WHERE d.assigned_unit_id IN ({placeholders})", conn, params=auth_nodes)
    st.dataframe(df, use_container_width=True)
else:
    dot = Digraph()
    dot.attr(rankdir='TB')
    # Set node shape to plaintext to allow custom HTML tables
    dot.attr('node', shape='plaintext', fontname='Inter')
    
    # 1. Fetch organizational nodes
    nodes = cursor.execute(f"SELECT node_id, node_name, parent_id FROM Org_Structure WHERE node_id IN ({placeholders})", auth_nodes).fetchall()
    
    # 2. Fetch all distributed assets for these nodes
    assets_query = f"SELECT assigned_unit_id, model_name, serial_number, status FROM Distributed_Assets WHERE assigned_unit_id IN ({placeholders})"
    assets_data = cursor.execute(assets_query, auth_nodes).fetchall()
    
    # Organize assets into a dictionary grouped by unit_id
    unit_assets = {}
    for uid, model, sn, status in assets_data:
        if uid not in unit_assets:
            unit_assets[uid] = []
        unit_assets[uid].append((model, sn, status))
        
    # 3. Build the HTML-table nodes
    for n_id, name, p_id in nodes:
        # Start HTML table definition
        html_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">
            <TR><TD COLSPAN="3" BGCOLOR="#0f172a"><FONT COLOR="#f8fafc"><B>{name}</B></FONT></TD></TR>'''
        
        # Populate table rows if unit has drones
        if n_id in unit_assets:
            html_label += '<TR><TD BGCOLOR="#f1f5f9"><B>Model</B></TD><TD BGCOLOR="#f1f5f9"><B>S/N</B></TD><TD BGCOLOR="#f1f5f9"><B>Status</B></TD></TR>'
            for model, sn, status in unit_assets[n_id]:
                # Color code the status text
                status_color = "#10b981" if status == 'Operational' else "#ef4444"
                html_label += f'<TR><TD>{model}</TD><TD>{sn}</TD><TD><FONT COLOR="{status_color}">{status}</FONT></TD></TR>'
        else:
            html_label += '<TR><TD COLSPAN="3" BGCOLOR="#ffffff"><FONT COLOR="#94a3b8"><I>No deployed assets</I></FONT></TD></TR>'
            
        html_label += '</TABLE>>'
        
        # Add the node and its connections
        dot.node(str(n_id), label=html_label)
        if p_id and p_id in auth_nodes: 
            dot.edge(str(p_id), str(n_id))
            
    st.graphviz_chart(dot)
