import sys
import os

# ---------------- PATH FIX ---------------- #
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

# ---------------- IMPORTS ---------------- #
import streamlit as st
import uuid
import time
import pyrebase

from app.core.orchestrator import multi_agent_system, generate_title
from app.core.database import save_chat, get_chats, get_all_sessions, rename_chat, delete_chat


# ---------------- PAGE CONFIG (MUST BE FIRST) ---------------- #
st.set_page_config(page_title="Multi-Agent AI", layout="wide")


# ---------------- FIREBASE AUTH ---------------- #
firebase_config = dict(st.secrets["firebase_web"])
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


# ---------------- SESSION INIT ---------------- #
if "user" not in st.session_state:
    st.session_state.user = None

if "login_success" not in st.session_state:
    st.session_state.login_success = False


# ---------------- LOGIN UI ---------------- #
if st.session_state.user is None:

    st.title("🔐 Login / Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # LOGIN
    with col1:
        if st.button("Login"):
            if not email or not password:
                st.warning("Enter email and password")
            else:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state.user = user
                    st.session_state.login_success = True
                    st.rerun()
                except Exception:
                    st.error("Invalid email or password")

    # SIGNUP
    with col2:
        if st.button("Signup"):
            if not email or not password:
                st.warning("Enter email and password")
            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("Account created! Please login.")
                except Exception:
                    st.error("Signup failed")

    # SUCCESS MESSAGE AFTER RERUN
    if st.session_state.login_success:
        st.success("Logged in successfully")
        st.session_state.login_success = False

    st.stop()


# ---------------- USER ID ---------------- #
user_id = st.session_state.user["localId"]


# ---------------- LOGOUT ---------------- #
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()


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
    st.write(f"👤 {st.session_state.user['email']}")

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

    sessions = get_all_sessions(user_id)

    for session_id, title in sessions:
        title_display = title if title else session_id[:8]

        if search_query.lower() in title_display.lower():

            col1, col2, col3 = st.columns([3, 1, 1])

            # OPEN CHAT
            if col1.button(title_display, key=session_id):
                st.session_state.session_id = session_id
                st.session_state.chat_title = title_display
                st.rerun()

            # EDIT
            if col2.button("✏️", key=f"edit_{session_id}"):
                st.session_state.editing_chat = session_id

            # DELETE
            if col3.button("🗑️", key=f"delete_{session_id}"):
                delete_chat(user_id, session_id)
                st.rerun()

            # RENAME UI
            if st.session_state.editing_chat == session_id:
                new_title = st.text_input(
                    "Rename chat",
                    value=title_display,
                    key=f"rename_input_{session_id}"
                )

                if st.button("Save", key=f"save_{session_id}"):
                    rename_chat(user_id, session_id, new_title)
                    st.session_state.editing_chat = None
                    st.rerun()


# ---------------- MAIN ---------------- #
st.markdown("<h1 style='text-align:center;'>🤖 Multi-Agent AI</h1>", unsafe_allow_html=True)

chat_history = get_chats(user_id, st.session_state.session_id)

for user, bot in chat_history:
    with st.chat_message("user"):
        st.markdown(user)
    with st.chat_message("assistant"):
        st.markdown(bot)


# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask something...")

if user_input:

    temp_mode = None

    if "short" in user_input.lower():
        temp_mode = "short"
    elif "detail" in user_input.lower():
        temp_mode = "detailed"

    final_mode = temp_mode if temp_mode else mode_selected

    if st.session_state.chat_title == "New Chat":
        st.session_state.chat_title = generate_title(user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        result = multi_agent_system(
            user_input,
            chat_history,
            final_mode
        )

    final_response = result["response"]
    agent_used = result["agent"]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""

        for word in final_response.split():
            text += word + " "
            placeholder.markdown(text)
            time.sleep(0.01)

        st.markdown(f"🧠 **Agent:** `{agent_used}`")

    # SAVE CHAT
    save_chat(
        user_id,
        st.session_state.session_id,
        st.session_state.chat_title,
        user_input,
        final_response
    )