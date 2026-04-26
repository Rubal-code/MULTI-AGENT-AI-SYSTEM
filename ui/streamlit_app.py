import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
import uuid
import time
import pyrebase

from app.core.orchestrator import multi_agent_system, generate_title
from app.core.database import save_chat, get_chats, get_all_sessions, rename_chat, delete_chat

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Multi-Agent AI", layout="wide")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>

/* Global background */
.stApp {
    background: #0f172a !important;
}

/* Hide default Streamlit header/footer */
header[data-testid="stHeader"] { display: none; }
footer { display: none; }

/* ── Auth page: center the middle column & give it a card look ── */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: transparent;
}

/* Target the auth form container via its block class */
.auth-wrapper {
    background: #1e293b;
    border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-top: 60px;
}

/* All text inside auth area */
.auth-heading {
    font-size: 22px;
    font-weight: 600;
    color: #f1f5f9;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
}
.auth-subheading {
    font-size: 14px;
    color: #64748b;
    margin: 0 0 1.5rem 0;
}
.auth-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.5rem;
}
.auth-brand-icon {
    width: 34px; height: 34px;
    background: #6366f1;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
}
.auth-brand-name {
    font-size: 15px; font-weight: 600;
    color: #f1f5f9; letter-spacing: -0.01em;
}
.auth-divider {
    height: 0.5px;
    background: rgba(255,255,255,0.07);
    margin: 0.5rem 0 1.25rem 0;
}
.auth-footer {
    text-align: center;
    font-size: 12px;
    color: #334155;
    margin-top: 1rem;
}

/* ── Input fields ── */
.stTextInput > label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #64748b !important;
    margin-bottom: 4px !important;
}
.stTextInput > div > div > input {
    background: #0f172a !important;
    border: 0.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
    padding: 10px 12px !important;
    height: 42px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    width: 100%;
    height: 42px;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border: none !important;
    transition: background 0.15s ease !important;
}

/* Primary (active tab / submit) */
button[kind="primary"] {
    background: #6366f1 !important;
    color: white !important;
}
button[kind="primary"]:hover {
    background: #4f46e5 !important;
}

/* Secondary (inactive tab) */
button[kind="secondary"] {
    background: transparent !important;
    border: 0.5px solid rgba(255,255,255,0.1) !important;
    color: #64748b !important;
}
button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.04) !important;
    color: #f1f5f9 !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 8px !important; font-size: 14px !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 0.5px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 0.5px solid rgba(255,255,255,0.08) !important;
    color: #cbd5e1 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 400 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: #6366f1 !important;
    color: #f1f5f9 !important;
}

/* ── Main chat title ── */
.main-title {
    text-align: center;
    color: #f1f5f9 !important;
    font-size: 26px;
    font-weight: 600;
    letter-spacing: -0.02em;
}

/* ── Chat messages ── */
.stChatMessage {
    background: #1e293b !important;
    border: 0.5px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE AUTH ---------------- #
firebase_config = dict(st.secrets["firebase_web"])
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ---------------- SESSION STATE ---------------- #
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"

# ================================================ #
# ---------------- LOGIN / SIGNUP UI ------------- #
# ================================================ #
if st.session_state.user is None:

    # Three-column layout → card lives in the middle column
    left, center, right = st.columns([1, 1.6, 1])

    with center:
        # ── Brand ──
        st.markdown("""
        <div class="auth-wrapper">
        <div class="auth-brand">
            <div class="auth-brand-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                     stroke="white" stroke-width="2.5" stroke-linecap="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <span class="auth-brand-name">Multi-Agent AI</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Heading ──
        if st.session_state.auth_tab == "login":
            st.markdown('<p class="auth-heading">Welcome back</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-subheading">Sign in to continue to your workspace</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="auth-heading">Create an account</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-subheading">Get started with Multi-Agent AI today</p>', unsafe_allow_html=True)

        # ── Tab switcher ──
        t1, t2 = st.columns(2)
        with t1:
            if st.button("Sign in", use_container_width=True,
                         type="primary" if st.session_state.auth_tab == "login" else "secondary",
                         key="tab_login"):
                st.session_state.auth_tab = "login"
                st.rerun()
        with t2:
            if st.button("Create account", use_container_width=True,
                         type="primary" if st.session_state.auth_tab == "signup" else "secondary",
                         key="tab_signup"):
                st.session_state.auth_tab = "signup"
                st.rerun()

        st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)

        # ── Fields ──
        email    = st.text_input("Email address", placeholder="you@example.com", key="auth_email")
        password = st.text_input("Password", type="password",
                                 placeholder="Enter your password", key="auth_password")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Action button ──
        if st.session_state.auth_tab == "login":
            if st.button("Sign in to workspace", use_container_width=True,
                         type="primary", key="btn_login"):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state.user = user
                    st.rerun()
                except:
                    st.error("Invalid email or password. Please try again.")
        else:
            if st.button("Create account", use_container_width=True,
                         type="primary", key="btn_signup"):
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("Account created! You can now sign in.")
                    st.session_state.auth_tab = "login"
                    st.rerun()
                except:
                    st.error("Signup failed. The email may already be in use.")

        st.markdown('<p class="auth-footer">Protected by end-to-end encryption</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # close auth-wrapper

    st.stop()

# ---------------- USER INFO ---------------- #
user_id = st.session_state.user["localId"]

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("### 💬 Chats")
    st.caption(f"Signed in as **{st.session_state.user['email']}**")
    st.divider()

    if st.button("🚪 Sign out", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    search_query = st.text_input("🔍 Search chats", placeholder="Search...")
    mode_selected = st.selectbox("Response mode", ["normal", "short", "detailed"])

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
        st.session_state.editing_chat = None
        st.rerun()

    st.divider()
    sessions = get_all_sessions(user_id)

    for session_id, title in sessions:
        title_display = title if title else session_id[:8]
        if search_query.lower() in title_display.lower():
            col1, col2, col3 = st.columns([3, 1, 1])
            if col1.button(title_display, key=session_id):
                st.session_state.session_id = session_id
                st.session_state.chat_title = title_display
                st.rerun()
            if col2.button("✏️", key=f"edit_{session_id}"):
                st.session_state.editing_chat = session_id
            if col3.button("🗑️", key=f"delete_{session_id}"):
                delete_chat(user_id, session_id)
                st.rerun()
            if st.session_state.get("editing_chat") == session_id:
                new_title = st.text_input("Rename", value=title_display,
                                          key=f"rename_input_{session_id}")
                if st.button("Save", key=f"save_{session_id}"):
                    rename_chat(user_id, session_id, new_title)
                    st.session_state.editing_chat = None
                    st.rerun()

# ---------------- SESSION INIT ---------------- #
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"
if "editing_chat" not in st.session_state:
    st.session_state.editing_chat = None

# ---------------- MAIN CHAT UI ---------------- #
st.markdown("<h1 class='main-title'>Multi-Agent AI</h1>", unsafe_allow_html=True)

chat_history = get_chats(user_id, st.session_state.session_id)

for user_msg, bot_msg in chat_history:
    with st.chat_message("user"):
        st.markdown(user_msg)
    with st.chat_message("assistant"):
        st.markdown(bot_msg)

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
        result = multi_agent_system(user_input, chat_history, final_mode)

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

    save_chat(
        user_id,
        st.session_state.session_id,
        st.session_state.chat_title,
        user_input,
        final_response
    )