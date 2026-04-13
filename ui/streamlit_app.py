import streamlit as st
import uuid # For generating unique session IDs
import time

from app.core.orchestrator import multi_agent_system
from app.core.database import save_chat, get_chats, get_all_sessions


st.set_page_config(page_title="Multi-Agent AI", layout="wide")

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("💬 Chat Sessions")

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if st.button("➕ New Chat"):
        st.session_state.session_id = str(uuid.uuid4())

    sessions = get_all_sessions()

    for s in sessions:
        if st.button(s[:8]):
            st.session_state.session_id = s

# ---------------- MAIN UI ---------------- #
st.markdown(
    """
    <h1 style='text-align: center;'>🤖 Multi-Agent AI Assistant</h1>
    """,
    unsafe_allow_html=True
)

# Chat container
chat_container = st.container()

# Load chat history
chat_history = get_chats(st.session_state.session_id)

with chat_container:
    for user, bot in chat_history:
        with st.chat_message("user"):
            st.markdown(user)

        with st.chat_message("assistant"):
            st.markdown(bot)

# ---------------- INPUT BOX ---------------- #
st.markdown("---")

user_input = st.chat_input("Ask something...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking... 🤔"):
        result = multi_agent_system(user_input, chat_history)

    final_response = f"""
### 📘 Summary:
{result['summary']}

### 🧠 Plan:
{result['plan']}
"""

    # 🔥 Streaming effect
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_text = ""

        for word in final_response.split():
            full_text += word + " "
            message_placeholder.markdown(full_text)
            time.sleep(0.03)

    save_chat(st.session_state.session_id, user_input, final_response)