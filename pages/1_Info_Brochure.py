import streamlit as st
import sqlite3
import pandas as pd
import os# pages/1_Info_Brochure.py
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="DIMS - Technical Dossier", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    .info-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .spec-badge {
        background-color: #f1f5f9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("DIMS - Drone Technical Dossier")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("SELECT model_name, role_type, flight_time, payload_capacity, technical_specs FROM Drone_Models")
    records = cursor.fetchall()
except sqlite3.OperationalError:
    records = []

if records:
    # Track looping indexes clean to fully evade the StreamlitDuplicateElementId bug
    for idx, row in enumerate(records):
        name, role, endurance, payload, raw_specs = row
        
        parsed_specs = raw_specs.split(" | Image: ")[0] if raw_specs and " | Image: " in raw_specs else raw_specs

        st.markdown(f"<div class='info-card'>", unsafe_allow_html=True)
        st.subheader(name)
        
        c1, c2, c3 = st.columns([1.5, 3, 2])
        with c1:
            st.markdown("<div style='background-color:#f8fafc; border:1px dashed #cbd5e1; height:140px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#94a3b8; font-size:12px;'>NO IMAGE AVAILABLE</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<span class='spec-badge'>Role: {role}</span>", unsafe_allow_html=True)
            st.write(f"**Max Flight Endurance:** {endurance}")
            st.write(f"**Payload Threshold Bound:** {payload}")
            st.write(f"**Schematic Parameters:** {parsed_specs}")
        with c3:
            st.markdown("<p style='font-size:12px; color:#64748b; font-weight:500; margin-bottom:4px;'>3D TELEMETRY MESH</p>", unsafe_allow_html=True)
            # UNIQUE ELEMENT ID KEY BINDING: Appending row index ensures identity uniqueness 
            st.button("VIEW STL MODEL (Phase 2)", disabled=True, use_container_width=True, key=f"btn_stl_render_{idx}")
            
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("The technical dossier registry is empty.")

conn.close()


st.set_page_config(page_title="Technical Dossier", layout="wide")

# --- UNIFIED TACTICAL CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1a1c24 !important; border-right: 2px solid #00d4ff1a; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Courier New'; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Tactical Drone Cards */
    .drone-card {
        background-color: #1a1c24;
        border: 1px solid #00d4ff33;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 20px;
        transition: border 0.3s ease;
    }
    .drone-card:hover {
        border: 1px solid #00d4ff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
    }
    .spec-label {
        color: #00d4ff;
        font-weight: bold;
        font-family: 'Courier New';
    }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ ACCESS DENIED: SECURE LOG IN REQUIRED")
    st.stop()

st.title("📡 DRONE TECHNICAL DOSSIER")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a local directory for media uploads if it doesn't exist
MEDIA_DIR = "drone_media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# --- ROLE CONSTRAINED ADMIN WORKFLOW (MANUFACTURER ONLY) ---
if st.session_state.role == 'Manufacturer':
    st.subheader("🛠️ FORWARD PLATFORM REGISTRATION (ADMIN)")
    with st.expander("➕ ADD NEW DRONE VARIANT TO REPOSITORY", expanded=False):
        with st.form("add_drone_variant", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                v_name = st.text_input("PLATFORM NAME DESIGNATION")
                v_role = st.text_input("OPERATIONAL SYSTEM ROLE (e.g., Loitering Munition)")
                v_flight = st.text_input("MAX ENDURANCE INDEX (e.g., 45 Mins)")
            with c2:
                v_payload = st.text_input("PAYLOAD CAPACITY LIMIT")
                v_specs = st.text_area("CORE TELEMETRY SCHEMATICS")
                uploaded_file = st.file_uploader("UPLOAD SYSTEM IMAGE (PNG/JPG)", type=["png", "jpg", "jpeg"])

            if st.form_submit_button("PUBLISH TO REGIMENTAL GRID"):
                if v_name and v_role:
                    # Handle Image Saving Path
                    image_path = "None"
                    if uploaded_file is not None:
                        # Clean filename to match asset nomenclature securely
                        clean_filename = f"{v_name.replace(' ', '_').lower()}_{uploaded_file.name}"
                        image_path = os.path.join(MEDIA_DIR, clean_filename)
                        with open(image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    try:
                        # Alter db execution slightly to check if image tracking strings exist or insert dynamically
                        cursor.execute("SELECT * FROM Drone_Models WHERE model_name=?", (v_name,))
                        if cursor.fetchone() is None:
                            # Note: We temporarily store image path references safely inside the SQLite structure
                            cursor.execute("""
                                INSERT INTO Drone_Models (model_name, role_type, flight_time, payload_capacity, technical_specs) 
                                VALUES (?,?,?,?,?)""", (v_name, v_role, v_flight, v_payload, f"{v_specs} | Image: {image_path}"))
                            conn.commit()
                            st.toast(f"SUCCESS: {v_name} synchronized across servers.")
                            st.rerun()
                        else:
                            st.error("Nomenclature collision: Asset name designation already logged.")
                    except Exception as e:
                        st.error(f"Database sync exception: {e}")
                else:
                    st.error("Mandatory platform fields must be processed.")

st.divider()

# --- INTUITIVE GRID VISUALIZATION FOR OPERATORS ---
st.subheader("📋 CURRENT FLEET BLUEPRINTS")

# Fetch current catalog records
cursor.execute("SELECT model_name, role_type, flight_time, payload_capacity, technical_specs FROM Drone_Models")
records = cursor.fetchall()

if records:
    for row in records:
        name, role, endurance, payload, raw_specs = row
        
        # Check if an image path was saved inside our text block
        parsed_specs = raw_specs
        img_url = None
        if " | Image: " in raw_specs:
            parts = raw_specs.split(" | Image: ")
            parsed_specs = parts[0]
            img_url = parts[1] if parts[1] != "None" else None

        # Build card layout framework matching layout
        with st.container():
            st.markdown(f"### ⚙️ {name}")
            col_img, col_data, col_3d = st.columns([1.5, 2.5, 2])
            
            with col_img:
                if img_url and os.path.exists(img_url):
                    st.image(img_url, use_container_width=True)
                else:
                    # Tactical static fall-back element block if no image is supplied
                    st.markdown("""
                        <div style='background-color: #262730; height: 160px; border: 1px dashed #00d4ff33; 
                        display: flex; align-items: center; justify-content: center; border-radius: 4px;'>
                            <span style='color: #666; font-family: monospace;'>NO IMAGING SIGNATURE REGISTERED</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col_data:
                st.markdown(f"<span class='spec-label'>FUNCTIONAL ROLE:</span> {role}", unsafe_allow_html=True)
                st.markdown(f"<span class='spec-label'>MAX ENDURANCE:</span> {endurance}", unsafe_allow_html=True)
                st.markdown(f"<span class='spec-label'>PAYLOAD BOUND:</span> {payload}", unsafe_allow_html=True)
                st.markdown(f"<span class='spec-label'>SCHEMATIC SPECIFICATIONS:</span>", unsafe_allow_html=True)
                st.write(parsed_specs)
                
            with col_3d:
                st.markdown("<span class='spec-label'>🛰️ 3D SPATIAL TELEMETRY</span>", unsafe_allow_html=True)
                # FUTURE PROSPECT HOOK: This block is structurally isolated to pipeline an STL parser
                st.info("💡 STL Component Mapping Ready. Upload 3D file layers in next phase to enable active mesh interactive viewer.")
                st.button("INITIALIZE RENDER PIPELINE", key=f"render_{name}", disabled=True)
                
            st.markdown("<hr style='border-top: 1px solid #00d4ff1a;'>", unsafe_allow_html=True)
else:
    st.info("System directories are empty. Awaiting core platform ingestion sequences.")

conn.close()
