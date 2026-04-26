import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ---------------- SAVE CHAT ---------------- #
def save_chat(user_id, session_id, title, user_input, response):
    db.collection("chats").add({
        "user_id": user_id,
        "session_id": session_id,
        "title": title,
        "user_input": user_input,
        "response": response
    })


# ---------------- GET CHATS ---------------- #
def get_chats(user_id, session_id):
    docs = db.collection("chats") \
        .where("user_id", "==", user_id) \
        .where("session_id", "==", session_id) \
        .stream()

    return [(doc.to_dict()["user_input"], doc.to_dict()["response"]) for doc in docs]


# ---------------- GET ALL SESSIONS ---------------- #
def get_all_sessions(user_id):
    docs = db.collection("chats") \
        .where("user_id", "==", user_id) \
        .stream()

    sessions = {}
    for doc in docs:
        data = doc.to_dict()
        sessions[data["session_id"]] = data["title"]

    return list(sessions.items())


# ---------------- DELETE ---------------- #
def delete_chat(user_id, session_id):
    docs = db.collection("chats") \
        .where("user_id", "==", user_id) \
        .where("session_id", "==", session_id) \
        .stream()

    for doc in docs:
        doc.reference.delete()


# ---------------- RENAME ---------------- #
def rename_chat(user_id, session_id, new_title):
    docs = db.collection("chats") \
        .where("user_id", "==", user_id) \
        .where("session_id", "==", session_id) \
        .stream()

    for doc in docs:
        doc.reference.update({"title": new_title})