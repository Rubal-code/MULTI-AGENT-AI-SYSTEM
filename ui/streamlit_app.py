import streamlit as st
import uuid

from app.core.orchestrator import multi_agent_system
from app.core.database import save_chat,get_chats,get_all_sessions

# import sys
# import os

# # Add project root to path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Multi-Agent-AI-System",page_icon=":robot_face:",layout="wide")

# title
st.title("🤖 Multi-Agent AI Assistant")
# sidebar
st.sidebar.title("💬 Chat Sessions")

if "session_id" not in st.session_state:
    st.session_state.session_id=str(uuid.uuid4())

if st.sidebar.button("➕ New Chat"):
    st.session_state.session_id=str(uuid.uuid4())

sessions=get_all_sessions()

for s in sessions:
    if st.sidebar.button(s[:8]):
        st.session_state.session_id=s

# Load chat history
chat_history = get_chats(st.session_state.session_id)

for user,bot in chat_history:
    st.chat_message("user").write(user)
    st.chat_message("assistant").write(bot)

# Input
user_input = st.chat_input("Ask something...")

if user_input:
    st.chat_message("user").write(user_input)
    result = multi_agent_system(user_input)

    final_response=f"**RESEARCH**\n{result['research']}\n\n**SUMMARY**\n{result['summary']}\n\n**PLAN**\n{result['plan']}"
    st.chat_message("assistant").write(final_response)
    save_chat(st.session_state.session_id, user_input,final_response)


# multi agent ai system to           python -m streamlit run ui/streamlit_app.py