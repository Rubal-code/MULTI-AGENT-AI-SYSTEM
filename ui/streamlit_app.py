import streamlit as st
import uuid
import time

from app.core.orchestrator import multi_agent_system
from app.core.database import save_chat, get_chats, get_all_sessions, rename_chat

st.set_page_config(page_title="Multi-Agent AI", layout="wide")



# ---------------- SESSION STATE ---------------- #
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

    if st.button("➕ New Chat"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
        st.session_state.editing_chat = None

    sessions = get_all_sessions()

    for session_id, title in sessions:
        title_display = title if title else session_id[:8]

        if search_query.lower() in title_display.lower():

            col1, col2 = st.columns([3,1])

            if col1.button(title_display, key=session_id):
                st.session_state.session_id = session_id
                st.session_state.chat_title = title_display
                st.session_state.editing_chat = None

            if col2.button("✏️", key=f"edit_{session_id}"):
                st.session_state.editing_chat = session_id

            if st.session_state.editing_chat == session_id:
                new_name = st.text_input("Rename chat:", key=f"rename_{session_id}")

                if st.button("Save", key=f"save_{session_id}"):
                    if new_name:
                        rename_chat(session_id, new_name)
                        st.session_state.chat_title = new_name
                        st.session_state.editing_chat = None
                        st.rerun()

# ---------------- MAIN ---------------- #
st.markdown("<h1 style='text-align:center;'>🤖 Multi-Agent AI Assistant</h1>", unsafe_allow_html=True)

chat_history = get_chats(st.session_state.session_id)

for user, bot in chat_history:
    with st.chat_message("user"):
        st.markdown(user)
    with st.chat_message("assistant"):
        st.markdown(bot)

# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask something...")

if user_input:

    if st.session_state.chat_title == "New Chat":
        st.session_state.chat_title = user_input[:30]

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking... 🤔"):
        result = multi_agent_system(user_input, chat_history)

    final_response = result["response"]

    # 🔥 Streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        for word in final_response.split():
            full_text += word + " "
            placeholder.markdown(full_text)
            time.sleep(0.02)

    save_chat(
        st.session_state.session_id,
        st.session_state.chat_title,
        user_input,
        final_response
    )