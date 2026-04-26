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

/* ── Global ── */
.stApp {
    background: #0f172a !important;
}
header[data-testid="stHeader"], footer { display: none !important; }

/* ── Make the CENTER column the card ──
   Target: 2nd column inside the horizontal block on the auth page */
div[data-testid="stHorizontalBlock"]
  > div[data-testid="stColumn"]:nth-child(2)
  > div[data-testid="stVerticalBlock"] {
    background: #1e293b;
    border: 0.5px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem 2rem !important;
    margin-top: 60px;
}

/* ── Input labels ── */
.stTextInput > label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #64748b !important;
}

/* ── Input boxes ── */
.stTextInput > div > div > input {
    background: #0f172a !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    height: 44px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.18) !important;
}

/* ── All buttons base ── */
.stButton > button {
    width: 100% !important;
    height: 44px !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s ease !important;
}

/* Primary = active tab / submit */
.stButton > button[kind="primary"] {
    background: #6366f1 !important;
    color: #ffffff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: #4f46e5 !important;
}

/* Secondary = inactive tab */
.stButton > button[kind="secondary"] {
    background: #0f172a !important;
    color: #64748b !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stButton > button[kind="secondary"]:hover {
    color: #f1f5f9 !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 13px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 0.5px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 0.5px solid rgba(255,255,255,0.07) !important;
    color: #94a3b8 !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: #6366f1 !important;
    color: #f1f5f9 !important;
}

/* ── Chat title ── */
.main-title {
    text-align: center;
    color: #f1f5f9 !important;
    font-size: 24px;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE AUTH ---------------- #
firebase_config = dict(st.secrets["firebase_web"])
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ---------------- SESSION STATE ---------------- #
if "user"      not in st.session_state: st.session_state.user      = None
if "auth_tab"  not in st.session_state: st.session_state.auth_tab  = "login"

# ================================================ #
# ────────────── LOGIN / SIGNUP UI ─────────────── #
# ================================================ #
if st.session_state.user is None:

    _, center, _ = st.columns([1, 1.4, 1])

    with center:

        # ── Brand row (pure HTML, no widget) ──
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;">
            <div style="width:38px;height:38px;background:#6366f1;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                     stroke="white" stroke-width="2.5" stroke-linecap="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <span style="font-size:16px;font-weight:600;color:#f1f5f9;letter-spacing:-0.01em;">
                Multi-Agent AI
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Heading (pure HTML) ──
        if st.session_state.auth_tab == "login":
            st.markdown("""
            <p style="font-size:26px;font-weight:700;color:#f1f5f9;
                      margin:0 0 4px;letter-spacing:-0.03em;">Welcome back</p>
            <p style="font-size:14px;color:#64748b;margin:0 0 1.5rem;">
                Sign in to your account to continue</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <p style="font-size:26px;font-weight:700;color:#f1f5f9;
                      margin:0 0 4px;letter-spacing:-0.03em;">Create an account</p>
            <p style="font-size:14px;color:#64748b;margin:0 0 1.5rem;">
                Get started with Multi-Agent AI today</p>
            """, unsafe_allow_html=True)

        # ── Tab switcher (Streamlit buttons) ──
        tc1, tc2 = st.columns(2)
        with tc1:
            if st.button("Sign in", use_container_width=True, key="tab_login",
                         type="primary" if st.session_state.auth_tab == "login" else "secondary"):
                st.session_state.auth_tab = "login"
                st.rerun()
        with tc2:
            if st.button("Create account", use_container_width=True, key="tab_signup",
                         type="primary" if st.session_state.auth_tab == "signup" else "secondary"):
                st.session_state.auth_tab = "signup"
                st.rerun()

        # ── Divider ──
        st.markdown("""
        <div style="height:0.5px;background:rgba(255,255,255,0.07);margin:1.25rem 0;"></div>
        """, unsafe_allow_html=True)

        # ── Input fields (Streamlit widgets — inside the same column = inside card) ──
        email    = st.text_input("Email address", placeholder="you@example.com",  key="auth_email")
        password = st.text_input("Password",      placeholder="Enter your password",
                                 type="password", key="auth_password")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

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
                    st.error("Signup failed. This email may already be registered.")

        # ── Footer note ──
        st.markdown("""
        <p style="text-align:center;font-size:12px;color:#334155;margin-top:1rem;margin-bottom:0;">
            Protected by end-to-end encryption
        </p>
        """, unsafe_allow_html=True)

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

    search_query  = st.text_input("🔍 Search chats", placeholder="Search...")
    mode_selected = st.selectbox("Response mode", ["normal", "short", "detailed"])

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.session_id   = str(uuid.uuid4())
        st.session_state.chat_title   = "New Chat"
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
if "session_id"   not in st.session_state: st.session_state.session_id   = str(uuid.uuid4())
if "chat_title"   not in st.session_state: st.session_state.chat_title   = "New Chat"
if "editing_chat" not in st.session_state: st.session_state.editing_chat = None

# ---------------- MAIN CHAT UI ---------------- #
st.markdown("<h1 class='main-title'>Multi-Agent AI</h1>", unsafe_allow_html=True)

chat_history = get_chats(user_id, st.session_state.session_id)
for user_msg, bot_msg in chat_history:
    with st.chat_message("user"):      st.markdown(user_msg)
    with st.chat_message("assistant"): st.markdown(bot_msg)

user_input = st.chat_input("Ask something...")
if user_input:
    temp_mode  = "short" if "short" in user_input.lower() else \
                 "detailed" if "detail" in user_input.lower() else None
    final_mode = temp_mode if temp_mode else mode_selected

    if st.session_state.chat_title == "New Chat":
        st.session_state.chat_title = generate_title(user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        result = multi_agent_system(user_input, chat_history, final_mode)

    final_response = result["response"]
    agent_used     = result["agent"]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""
        for word in final_response.split():
            text += word + " "
            placeholder.markdown(text)
            time.sleep(0.01)
        st.markdown(f"🧠 **Agent:** `{agent_used}`")

    save_chat(user_id, st.session_state.session_id,
              st.session_state.chat_title, user_input, final_response)