import streamlit as stimport streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="DIMS - AI Copilot", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    h1, h2, h3, h4 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    if st.session_state.get('logged_in', False):
        st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
        st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
        st.page_link("pages/5_AI_Assistant.py", label="🤖 AI Assistant", use_container_width=True)
        st.divider()
        st.markdown(f"User: **{st.session_state.username}**")

# --- AI LOGIC ---
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Authentication required.")
else:
    st.markdown("<h1>🤖 DIMS AI Logistics Copilot</h1>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Copilot online. How can I assist with logistics?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about Navastra specs..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # ACCESSING THE SECURE KEY
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("Configuration Error: Ensure GEMINI_API_KEY is set in Streamlit Secrets.")

import google.generativeai as genai

st.set_page_config(page_title="DIMS - AI Copilot", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Stylesheet to maintain the clean light-theme layout
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    h1, h2, h3, h4 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    
    /* Chat Input Styling */
    .stChatInputContainer { padding-bottom: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation & API Key Input
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-top:0; margin-bottom:24px;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    if st.session_state.get('logged_in', False):
        st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
        st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
        st.page_link("pages/2_Distribution.py", label="🚛 Fleet Deployment", use_container_width=True)
        st.page_link("pages/3_Inventory.py", label="🛠️ Inventory & Assembly", use_container_width=True)
        # Adjust the filename below to exactly match your AI assistant python file
        st.page_link("pages/5_AI_Assistant.py", label="🤖 AI Assistant", use_container_width=True)
        
        st.divider()
        st.markdown("<p style='font-size:13px; color:#64748b; margin-bottom:4px;'>Copilot Configuration:</p>", unsafe_allow_html=True)
        api_key = st.text_input("Enter Gemini API Key", type="password", placeholder="AIzaSy...")
        
        st.divider()
        st.markdown(f"<p style='font-size:13px; color:#64748b; margin-bottom:0;'>User Profile:</p><strong style='color:#0f172a;'>{st.session_state.username} ({st.session_state.role})</strong>", unsafe_allow_html=True)

# Main Application Logic
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Access Denied. Secure session authentication required on the Dashboard Console.")
else:
    st.markdown("<h1>🤖 DIMS AI Logistics Copilot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top: -10px; margin-bottom: 24px;'>Ask questions about fleet technical specifications, inventory thresholds, or procurement protocols.</p>", unsafe_allow_html=True)

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome to the DIMS AI Copilot. How can I assist you with drone inventory, Navastra deployments, or tactical logistics today?"}
        ]

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input Field
    if prompt := st.chat_input("Ask about Navastra specs, stock levels, or operational procedures..."):
        
        # Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process API Response
        if not api_key:
            error_msg = "⚠️ I am currently operating in offline mode. Please enter your Gemini API key in the sidebar to enable live logistical analysis."
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            try:
                # Configure Gemini API
                genai.configure(api_key=api_key)
                
                # Define system context to ground the AI in your specific logistics domain
                system_instruction = """
                You are the AI Logistics Copilot for DIMS (Drone Inventory Management System). 
                You assist military and technical personnel with managing Unmanned Aerial Vehicles (UAVs).
                Key assets include the NAVASTRA 51 (Surveillance, 60min endurance, 2.5kg payload) and 
                NAVASTRA 81 (Heavy Payload/Loitering, 40min endurance, 12kg payload), as well as payload droppers 
                and kamikaze variants. Provide concise, professional, and highly technical logistical advice.
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
                
                # Format history for the Gemini SDK (omitting the first system greeting for clean API passing)
                gemini_history = []
                for msg in st.session_state.messages[1:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})

                # Stream response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing logistics database..."):
                        chat = model.start_chat(history=gemini_history)
                        response = chat.send_message(prompt)
                        st.markdown(response.text)
                        
                # Save assistant response to memory
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"Authentication or Connection Breach: {e}")
