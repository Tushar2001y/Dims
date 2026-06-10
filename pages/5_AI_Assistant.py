import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="DIMS - AI Copilot", layout="wide", initial_sidebar_state="expanded")

# Inject Custom Stylesheet to maintain the clean light-theme layout
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
    h1, h2, h3, h4 { color: #0f172a !important; font-family: 'Inter', -apple-system, sans-serif !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# Shared Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb !important; margin-bottom:0;'>📦 D-dims</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:12px; margin-top:0; margin-bottom:24px;'>Drone Inventory Management System</p>", unsafe_allow_html=True)
    
    if st.session_state.get('logged_in', False):
        st.page_link("Home.py", label="📊 Dashboard Console", use_container_width=True)
        st.page_link("pages/1_Info_Brochure.py", label="📡 Technical Dossier", use_container_width=True)
        st.page_link("pages/2_Distribution.py", label="🚛 Fleet Deployment", use_container_width=True)
        st.page_link("pages/3_Inventory.py", label="🛠️ Inventory & Assembly", use_container_width=True)
        st.page_link("pages/5_AI_Assistant.py", label="🤖 AI Assistant", use_container_width=True)
        st.divider()
        st.markdown(f"User Profile: **{st.session_state.username}**")

# Main Application Logic
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Access Denied. Secure session authentication required on the Dashboard Console.")
else:
    st.markdown("<h1>🤖 DIMS AI Logistics Copilot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-top: -10px; margin-bottom: 24px;'>Ask questions about fleet technical specifications, inventory thresholds, or procurement protocols.</p>", unsafe_allow_html=True)

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Copilot online. How can I assist you with drone inventory or tactical logistics today?"}
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

        try:
            # 1. Verify that the Secret key exists in Streamlit Cloud Settings
            if "GROQ_API_KEY" not in st.secrets:
                st.error("Missing GROQ_API_KEY in Streamlit Secrets. Please add it to your App Settings.")
                st.stop()
                
            # 2. Extract the key securely from env block
            secret_key = st.secrets["GROQ_API_KEY"]
            
            # Route requests through Groq infrastructure using OpenAI standard client
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=secret_key
            )
            
            # Pack history cleanly for API execution
            messages_payload = [
                {
                    "role": "system",
                    "content": "You are the AI Logistics Copilot for DIMS. You manage military drone arrays including the NAVASTRA 51 and NAVASTRA 81. Keep solutions short, structured, and professional."
                }
            ]
            
            for msg in st.session_state.messages:
                messages_payload.append({"role": msg["role"], "content": msg["content"]})

            # Stream response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing parameters..."):
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192", 
                        messages=messages_payload,
                    )
                    response_text = completion.choices[0].message.content
                    st.markdown(response_text)
                    
            # Save assistant response to memory
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"System Error: {e}")
