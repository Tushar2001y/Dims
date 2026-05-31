import streamlit as st
import sqlite3
import os

st.set_page_config(layout="wide")

# Secure access: Only Manufacturer can edit
is_admin = st.session_state.get('role') == 'Manufacturer'

st.title("📡 DRONE TECHNICAL DOSSIER")

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

if is_admin:
    with st.expander("➕ REGISTER NEW PLATFORM", expanded=False):
        with st.form("add_drone"):
            name = st.text_input("PLATFORM NAME")
            role = st.text_input("ROLE")
            img = st.file_uploader("UPLOAD SYSTEM IMAGE", type=['png', 'jpg', 'jpeg'])
            specs = st.text_area("TECHNICAL SPECS")
            if st.form_submit_button("SAVE TO DOSSIER"):
                img_path = f"drone_media/{name}.png" if img else ""
                if img:
                    if not os.path.exists("drone_media"): os.makedirs("drone_media")
                    with open(img_path, "wb") as f: f.write(img.getbuffer())
                
                cursor.execute("INSERT INTO Drone_Models (model_name, role_type, technical_specs, image_path) VALUES (?,?,?,?)", 
                               (name, role, specs, img_path))
                conn.commit()
                st.rerun()

# Display Grid
drones = cursor.execute("SELECT model_name, role_type, technical_specs, image_path FROM Drone_Models").fetchall()
for d in drones:
    with st.container():
        c1, c2, c3 = st.columns([1.5, 2, 1.5])
        with c1:
            if d[3] and os.path.exists(d[3]): st.image(d[3])
            else: st.info("NO IMAGE AVAILABLE")
        with c2:
            st.subheader(d[0])
            st.caption(f"Role: {d[1]}")
            st.write(d[2])
        with c3:
            st.markdown("**3D TELEMETRY**")
            st.button("VIEW STL MODEL (Phase 2)", disabled=True, use_container_width=True)
        st.divider()
conn.close()
