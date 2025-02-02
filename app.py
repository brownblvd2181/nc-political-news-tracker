import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# 🔥 Load Firebase Credentials from Streamlit Secrets
firebase_secrets = st.secrets["firebase"]
firebase_creds = {
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
}

# 🔐 Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {"databaseURL": "https://nc-policy-tracker.firebaseio.com"})  # Replace with your actual Firebase DB URL

