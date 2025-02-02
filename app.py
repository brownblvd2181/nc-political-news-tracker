import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import nltk
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh  # Auto-refresh for the News page

# Force Download NLTK 'punkt' if missing (prevents LookupError)
nltk_data_path = os.path.expanduser("~/nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)
nltk.download("punkt", download_dir=nltk_data_path)
nltk.download("stopwords", download_dir=nltk_data_path)

# Define Politician Images
POLITICIAN_IMAGES = {
    "Alma Adams": "https://upload.wikimedia.org/wikipedia/commons/3/30/Alma_Adams_117th_U.S_Congress.jpg",
    "Don Davis": "https://upload.wikimedia.org/wikipedia/commons/7/7e/RepDonDavis.jpg",
    "Mayor Vi Lyles": "https://upload.wikimedia.org/wikipedia/commons/2/2a/MayorViLyles.png",
    "Mayor Karen Bass": "https://upload.wikimedia.org/wikipedia/commons/d/db/Karen_Bass_official_portrait_as_mayor_of_Los_Angeles.jpg"
}

# Define Google News RSS feeds
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
    "Mayor Vi Lyles": "https://news.google.com/rss/search?q=Mayor+Vi+Lyles+Charlotte",
    "Mayor Karen Bass": "https://news.google.com/rss/search?q=Mayor+Karen+Bass"
}

def get_news(person, keyword="", limit=5):
    """Fetch news and perform sentiment analysis."""
    feed_url = URLS.get(person)
    if not feed_url:
        return []
    
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"Error fetching data from {feed_url}: {e}")
        return []

    # Parse RSS feed with lxml-xml
    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:limit]:
        title = item.title.text if item.title else "No Title"
        pub_date = item.pubDate.text if item.pubDate else "Unknown Date"

        # Filter by keyword
        if keyword and keyword.lower() not in title.lower():
            continue

        # Sentiment Analysis using TextBlob
        sentiment_score = TextBlob(title).sentiment.polarity
        sentiment = "Neutral"
        if sentiment_score > 0:
            sentiment = "Positive"
        elif sentiment_score < 0:
            sentiment = "Negative"

        image_url = POLITICIAN_IMAGES.get(person, "")

        articles.append({
            "Title": title,
            "Link": item.link.text if item.link else "",
            "Published": pub_date,
            "Image": image_url,
            "Sentiment": sentiment
        })
    return articles

def generate_trending_topics(news_articles):
    """Generate a word cloud for trending political topics."""
    nltk.download("punkt", download_dir=nltk_data_path)  # Ensure 'punkt' is available
    nltk.download("stopwords", download_dir=nltk_data_path)

    all_titles = " ".join([article["Title"] for article in news_articles])
    words = word_tokenize(all_titles)
    words = [word.lower() for word in words if word.isalnum()]
    words = [word for word in words if word not in stopwords.words("english")]

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(words))

    # Display Word Cloud
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# Streamlit page config
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Sidebar Navigation
page = st.sidebar.radio("Select Page:", ["News", "Videos", "AI Reports"])

if page == "News":
    st_autorefresh(interval=60000, limit=100, key="news_refresh")

    # Sidebar for News Filters
    st.sidebar.markdown("## 🔍 Filter News")
    selected_politicians = st.sidebar.multiselect(
        "Select Politician(s)", list(URLS.keys()), default=list(URLS.keys())
    )
    keyword = st.sidebar.text_input("Search for a topic (optional):")
    news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

    # Main News Page
    st.title("🗳️ NC Political News Tracker - News")

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
                        st.markdown(f"### {article['Title']} ({article['Sentiment']})")
                        st.markdown(f"🕒 {article['Published']}")
                        st.markdown(f"[🔗 Read More]({article['Link']})")
            else:
                st.warning(f"No recent news found for {person}.")

elif page == "Videos":
    st.title("🎥 Politician Videos")
    st.video("https://youtu.be/Ze0jW_ysAJ0?si=uddnUb_QeDiZNEDH")
    st.video("https://youtu.be/QFiLuZqyr4E?si=JLetW56-RsxU5dPd")
    st.video("https://youtu.be/HZv_GhJ8RFI?si=BoM_Wbfnrl1dH7H3")
    st.video("https://youtu.be/Oj7BsVWziMA?si=tXvZcwY2qvvC0U-G")

elif page == "AI Reports":
    st.title("📊 AI-Powered Sentiment & Trending Reports")

    # Fetch all news articles for analysis
    all_articles = []
    for person in URLS.keys():
        all_articles.extend(get_news(person, limit=10))

    if all_articles:
        st.markdown("### 🏆 Political Sentiment Analysis")
        sentiment_counts = pd.DataFrame(pd.Series([a["Sentiment"] for a in all_articles]).value_counts(), columns=["Count"])
        st.bar_chart(sentiment_counts)

        st.markdown("### 🔥 Trending Political Topics")
        generate_trending_topics(all_articles)
    else:
        st.warning("No articles available for analysis.")


