import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page first.")
else:
    st.title("Drone Info Brochure")
    st.write(f"Logged in as: {st.session_state.role}")
