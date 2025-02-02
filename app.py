import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
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

# 🔐 Initialize Firebase with Secure Credentials
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {"databaseURL": "https://your-firebase-db.firebaseio.com"})  # Replace with your actual Firebase DB URL

# 🔎 Define News Sources
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
    "Mayor Vi Lyles": "https://news.google.com/rss/search?q=Mayor+Vi+Lyles+Charlotte",
    "Mayor Karen Bass": "https://news.google.com/rss/search?q=Mayor+Karen+Bass"
}

# 🔄 Streamlit Navigation
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")
page = st.sidebar.radio("Select Page:", ["News", "Videos", "Community Forum"])

# 🔥 Fetch News Function
def get_news(person, keyword="", limit=5):
    feed_url = URLS.get(person)
    if not feed_url:
        return []

    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"⚠️ Error fetching data from {feed_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:limit]:
        title = item.title.text if item.title else "No Title"
        pub_date = item.pubDate.text if item.pubDate else "Unknown Date"

        articles.append({
            "Title": title,
            "Link": item.link.text if item.link else "",
            "Published": pub_date,
        })
    return articles

# 📰 News Page
if page == "News":
    st.title("🗳️ NC Political News Tracker - News")
    selected_politicians = st.sidebar.multiselect("Select Politician(s)", list(URLS.keys()), default=list(URLS.keys()))
    keyword = st.sidebar.text_input("Search for a topic (optional):")
    news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

    if selected_politicians:
        for person in selected_politicians:
            news_articles = get_news(person, keyword=keyword, limit=news_limit)
            if news_articles:
                st.markdown(f"## 📰 Latest News on {person}")
                for article in news_articles:
                    st.markdown(f"### [{article['Title']}]({article['Link']})")
                    st.markdown(f"🕒 {article['Published']}")
            else:
                st.warning(f"⚠️ No recent news found for {person}.")

