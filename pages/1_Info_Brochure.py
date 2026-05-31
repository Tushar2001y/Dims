import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="Technical Dossier", layout="wide")
st.markdown("<style>.stApp { background-color: #0e1117; } h1, h3 { color: #00d4ff !important; }</style>", unsafe_allow_html=True)

if not st.session_state.get('logged_in'): st.stop()

st.title("📡 DRONE TECHNICAL DOSSIER")
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Admin Upload Section
if st.session_state.role == 'Manufacturer':
    with st.expander("➕ REGISTER NEW PLATFORM", expanded=False):
        with st.form("new_drone"):
            name = st.text_input("Name")
            role = st.text_input("Role")
            specs = st.text_area("Technical Specs")
            img = st.file_uploader("Upload Image", type=['png', 'jpg'])
            if st.form_submit_button("PUBLISH"):
                path = "None"
                if img:
                    path = f"drone_media/{img.name}"
                    with open(path, "wb") as f: f.write(img.getbuffer())
                cursor.execute("INSERT INTO Drone_Models (model_name, role_type, technical_specs, image_path) VALUES (?,?,?,?)", (name, role, specs, path))
                conn.commit()
                st.rerun()

# Display Section
records = cursor.execute("SELECT model_name, role_type, technical_specs, image_path FROM Drone_Models").fetchall()
for r in records:
    with st.container():
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            if r[3] != "None" and os.path.exists(r[3]): st.image(r[3])
            else: st.info("No Image")
        with col2:
            st.subheader(r[0])
            st.write(f"**Role:** {r[1]}")
            st.write(r[2])
        with col3:
            st.markdown("**3D TELEMETRY**")
            st.button("INITIALIZE 3D RENDER", key=f"btn_{r[0]}", disabled=True)
        st.divider()
conn.close()
