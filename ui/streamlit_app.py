import streamlit as st
import uuid
import time

from app.core.orchestrator import multi_agent_system, generate_title
from app.core.database import save_chat, get_chats, get_all_sessions, rename_chat, delete_chat
import sys
import os

#  FIX IMPORT PATH FOR STREAMLIT CLOUD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Multi-Agent AI", layout="wide")


# ---------------- SESSION ---------------- #
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

if "editing_chat" not in st.session_state:
    st.session_state.editing_chat = None


# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("💬 Chats")

    search_query = st.text_input("🔍 Search chats")

    mode_selected = st.selectbox(
        "Response Mode",
        ["normal", "short", "detailed"]
    )

    if st.button("➕ New Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
        st.session_state.editing_chat = None
        st.rerun()

    sessions = get_all_sessions()

    for session_id, title in sessions:
        title_display = title if title else session_id[:8]

        if search_query.lower() in title_display.lower():

            col1, col2, col3 = st.columns([3,1,1])

            if col1.button(title_display, key=session_id):
                st.session_state.session_id = session_id
                st.session_state.chat_title = title_display
                st.rerun()

            if col2.button("✏️", key=f"edit_{session_id}"):
                st.session_state.editing_chat = session_id

            if col3.button("🗑️", key=f"delete_{session_id}"):
                delete_chat(session_id)
                st.rerun()


# ---------------- MAIN ---------------- #
st.markdown("<h1 style='text-align:center;'>🤖 Multi-Agent AI</h1>", unsafe_allow_html=True)

chat_history = get_chats(st.session_state.session_id)

for user, bot in chat_history:
    with st.chat_message("user"):
        st.markdown(user)
    with st.chat_message("assistant"):
        st.markdown(bot)


# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask something...")

if user_input:

    # 🔥 TEMP MODE (NO STICKY MEMORY)
    temp_mode = None

    if "short" in user_input.lower():
        temp_mode = "short"

    elif "detail" in user_input.lower() or "explain more" in user_input.lower():
        temp_mode = "detailed"

    # 🔥 FINAL MODE DECISION
    final_mode = temp_mode if temp_mode else mode_selected

    # 🔥 Title
    if st.session_state.chat_title == "New Chat":
        st.session_state.chat_title = generate_title(user_input)

    # Show user
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI response
    with st.spinner("Thinking..."):
        result = multi_agent_system(
            user_input,
            chat_history,
            final_mode
        )

    final_response = result["response"]
    agent_used = result["agent"]

    # Streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""

        for word in final_response.split():
            text += word + " "
            placeholder.markdown(text)
            time.sleep(0.01)

        st.markdown(f"🧠 **Agent:** `{agent_used}`")

    save_chat(
        st.session_state.session_id,
        st.session_state.chat_title,
        user_input,
        final_response
    )