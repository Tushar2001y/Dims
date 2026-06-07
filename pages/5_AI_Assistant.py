# pages/5_AI_Assistant.py
import streamlit as st
import time

st.set_page_config(page_title="DIMS - AI Assistant", layout="wide")

# --- UNIFIED DASHBOARD CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Inter', sans-serif; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Access Denied: Secure Login Required")
    st.stop()

st.title("🤖 DIMS AI Logistics Copilot")
st.markdown("Ask questions about fleet technical specifications, inventory thresholds, or procurement protocols.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the DIMS AI Copilot. How can I assist you with drone inventory or tactical logistics today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about Navastra specs, stock levels, or operational procedures..."):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- AI RESPONSE GENERATION ---
    # NOTE: You can replace this block with an actual API call (e.g., Google Gemini or OpenAI)
    # response = gemini_client.generate_content(prompt)
    
    # Simulated AI logic for the UI demonstration
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Simple simulated routing based on keywords
        if "navastra 51" in prompt.lower():
            ai_reply = "The **Navastra 51** is optimized for Surveillance & Target Acquisition. It has a 60-minute flight time and a 2.5 kg payload capacity featuring an EO/IR sensor and anti-jamming GPS. Are you looking to assemble one or check stock?"
        elif "stock" in prompt.lower() or "inventory" in prompt.lower():
            ai_reply = "To view live stock levels, please navigate to the **Inventory & Assembly** page using the left sidebar. Critical shortages are highlighted in red."
        else:
            ai_reply = f"I am currently operating in offline mode. I received your query: '{prompt}'. Connect an API key to enable live database querying and advanced logistical analysis."
        
        # Simulate typing effect
        for chunk in ai_reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
