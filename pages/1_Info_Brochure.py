import streamlit as st

st.set_page_config(page_title="DIMS - Technical Dossier", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Stylesheet matching the main Home Console light layout
st.markdown("""
    <style>
    /* Global Background & Core Text Adjustments */
    .stApp { background-color: #f8fafc; color: #0f172a; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    
    /* Typography Alignment */
    h1, h2, h3, h4 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    
    /* Tech Specs Container Custom Cards */
    .tech-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 24px;
    }
    .spec-label { color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }
    .spec-value { color: #0f172a; font-size: 15px; margin-bottom: 12px; font-weight: 500; }
    
    /* Placeholder Display Block */
    .image-placeholder {
        background-color: #f1f5f9;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
        font-weight: 500;
        font-size: 13px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# Shared Sidebar Navigation (Matches Home Console)
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-top:0; margin-bottom:24px;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    if st.session_state.get('logged_in', False):
        st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
        st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
        st.page_link("pages/2_Distribution.py", label="🚛 Fleet Deployment", use_container_width=True)
        st.page_link("pages/3_Inventory.py", label="🛠️ Inventory & Assembly", use_container_width=True)
        st.divider()
        st.markdown(f"<p style='font-size:13px; color:#64748b; margin-bottom:0;'>User Profile:</p><strong style='color:#0f172a;'>{st.session_state.username} ({st.session_state.role})</strong>", unsafe_allow_html=True)

# Main Page Layout Verification
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Access Denied. Please clear authentication on the Dashboard Console.")
else:
    st.markdown("<h1>Drone Technical Dossier</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top: -10px; margin-bottom: 24px;'>Hardware configurations, sensor architecture profiles, and 3D schematic layers.</p>", unsafe_allow_html=True)
    
    st.markdown("<h2>📋 Current Fleet Blueprints</h2>", unsafe_allow_html=True)
    st.divider()
    
    # ------------------ NAVASTRA 51 SECTION ------------------
    st.markdown("<h3 style='color: #2563eb !important;'>⚙️ NAVASTRA 51</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.2, 2, 1.5])
        
        with col1:
            st.markdown("<div class='image-placeholder'>No Imaging Signature Registered</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<span class='spec-label'>Functional Role</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>Surveillance & Target Acquisition</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Max Flight Endurance</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>60 Minutes</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Payload Threshold Bound</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>2.5 kg</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Schematic Parameters</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>EO/IR sensor payload, encrypted 5G telemetry, anti-jamming GPS module.</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("🌐 **3D SPATIAL TELEMETRY**")
            st.info("💡 STL Component Mapping Ready. Upload 3D file layers in next phase to enable active mesh interactive viewer.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    # ------------------ NAVASTRA 81 SECTION ------------------
    st.markdown("<h3 style='color: #2563eb !important;'>⚙️ NAVASTRA 81</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.2, 2, 1.5])
        
        with col1:
            st.markdown("<div class='image-placeholder'>No Imaging Signature Registered</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<span class='spec-label'>Functional Role</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>Heavy Payload / Loitering Munition</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Max Flight Endurance</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>40 Minutes</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Payload Threshold Bound</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>12 kg</div>", unsafe_allow_html=True)
            
            st.markdown("<span class='spec-label'>Schematic Parameters</span>", unsafe_allow_html=True)
            st.markdown("<div class='spec-value'>Terminal guidance, extended range antenna, modular payload bay.</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("🌐 **3D SPATIAL TELEMETRY**")
            st.info("💡 STL Component Mapping Ready. Upload 3D file layers in next phase to enable active mesh interactive viewer.")
            
        st.markdown("</div>", unsafe_allow_html=True)
