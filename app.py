import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

# 🔥 Initialize Firebase (Make sure firebase-credentials.json is in the same folder)
cred = credentials.Certificate("firebase-credentials.json")  
firebase_admin.initialize_app(cred, {"databaseURL": "https://your-firebase-db.firebaseio.com"})  # Replace with your database URL

# 🔎 Define News Sources
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
    "Mayor Vi Lyles": "https://news.google.com/rss/search?q=Mayor+Vi+Lyles+Charlotte",
    "Mayor Karen Bass": "https://news.google.com/rss/search?q=Mayor+Karen+Bass"
}

# 📸 Define Politician Images
POLITICIAN_IMAGES = {
    "Alma Adams": "https://upload.wikimedia.org/wikipedia/commons/3/30/Alma_Adams_117th_U.S_Congress.jpg",
    "Don Davis": "https://upload.wikimedia.org/wikipedia/commons/7/7e/RepDonDavis.jpg",
    "Mayor Vi Lyles": "https://upload.wikimedia.org/wikipedia/commons/2/2a/MayorViLyles.png",
    "Mayor Karen Bass": "https://upload.wikimedia.org/wikipedia/commons/d/db/Karen_Bass_official_portrait_as_mayor_of_Los_Angeles.jpg"
}

# 📡 Fetch News Function
def get_news(person, keyword="", limit=5):
    """Fetch news articles for the given politician."""
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

        image_url = POLITICIAN_IMAGES.get(person, "")

        articles.append({
            "Title": title,
            "Link": item.link.text if item.link else "",
            "Published": pub_date,
            "Image": image_url
        })
    return articles

# 🏠 Streamlit Page Config
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# 🗂️ Sidebar Navigation
page = st.sidebar.radio("Select Page:", ["News", "Videos", "Community Forum"])

# 📰 News Page
if page == "News":
    st.title("🗳️ NC Political News Tracker - News")

    # 🔍 Sidebar Filters
    selected_politicians = st.sidebar.multiselect("Select Politician(s)", list(URLS.keys()), default=list(URLS.keys()))
    keyword = st.sidebar.text_input("Search for a topic (optional):")
    news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

    if selected_politicians:
        for person in selected_politicians:
            news_articles = get_news(person, keyword=keyword, limit=news_limit)
            if news_articles:
                st.markdown(f"## 📰 Latest News on {person}")
                for article in news_articles:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(article["Image"], use_container_width=True)
                    with col2:
                        st.markdown(f"### [{article['Title']}]({article['Link']})")
                        st.markdown(f"🕒 {article['Published']}")
            else:
                st.warning(f"⚠️ No recent news found for {person}.")

# 🎥 Videos Page
elif page == "Videos":
    st.title("🎥 Politician Videos")
    
    video_data = {
        "Alma Adams": "https://youtu.be/Ze0jW_ysAJ0?si=uddnUb_QeDiZNEDH",
        "Don Davis": "https://youtu.be/QFiLuZqyr4E?si=JLetW56-RsxU5dPd",
        "Mayor Vi Lyles": "https://youtu.be/HZv_GhJ8RFI?si=BoM_Wbfnrl1dH7H3",
        "Mayor Karen Bass": "https://youtu.be/Oj7BsVWziMA?si=tXvZcwY2qvvC0U-G"
    }
    
    for person, video_url in video_data.items():
        st.markdown(f"## 🎥 {person}'s Recent Video")
        st.video(video_url)

# 💬 Community Forum (Using Firebase)
elif page == "Community Forum":
    st.title("💬 Community Forum - Political Discussions")
    st.markdown("Discuss the latest political topics below!")

    # 🔄 Fetch Comments from Firebase
    ref = db.reference("comments")
    comments = ref.get()

    if comments:
        for key, comment in comments.items():
            st.markdown(f"**{comment['username']}**: {comment['comment']}")

    # 📝 Add New Comment
    username = st.text_input("Your Name:")
    comment_text = st.text_area("Write your comment:")

    if st.button("Submit Comment"):
        if username and comment_text:
            ref.push({"username": username, "comment": comment_text})
            st.success("✅ Your comment has been posted!")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Please enter your name and comment before submitting.")


