import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Define a single RSS feed (Google News) for each politician
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
    "Mayor Vi Lyles": "https://news.google.com/rss/search?q=Mayor+Vi+Lyles+Charlotte",
    "Mayor Karen Bass": "https://news.google.com/rss/search?q=Mayor+Karen+Bass"
}

DEFAULT_IMAGE = "https://via.placeholder.com/150/3498db/ffffff?text=News"  # Default thumbnail

def get_news(person, keyword="", limit=5):
    """
    Fetch the top news articles for the given person from the Google News RSS feed.
    Optionally filter articles by a keyword.
    """
    feed_url = URLS.get(person)
    if not feed_url:
        return []
    
    try:
        response = requests.get(feed_url, timeout=10)
    except Exception as e:
        st.warning(f"Error fetching data from {feed_url}: {e}")
        return []
    
    soup = BeautifulSoup(response.content, "xml")
    articles = []
    for item in soup.find_all("item")[:limit]:
        title = item.title.text
        
        # Apply keyword filter if a keyword is provided
        if keyword and keyword.lower() not in title.lower():
            continue
        
        articles.append({
            "Title": title,
            "Link": item.link.text,
            "Published": item.pubDate.text if item.pubDate else "Unknown Date",
            "Image": DEFAULT_IMAGE
        })
    return articles

def save_email(email):
    """Save an email address to a CSV file for daily newsletter subscriptions."""
    with open("subscribers.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email])
    return True

# Streamlit UI configuration
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Custom CSS for styling and improved readability
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        body { 
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa;
        }
        .news-container {
            padding: 15px;
            border-radius: 12px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .news-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .news-meta {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }
        .news-link {
            font-size: 16px;
            color: #2980b9;
            font-weight: bold;
            text-decoration: none;
        }
        .news-link:hover {
            text-decoration: underline;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation and Email Subscription
st.sidebar.markdown("## 🔍 Filter News")
selected_politicians = st.sidebar.multiselect(
    "Select Politician(s)", list(URLS.keys()), default=list(URLS.keys())
)
keyword = st.sidebar.text_input("Search for a topic (optional):")
news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

st.sidebar.markdown("## 📩 Subscribe for Daily News")
email = st.sidebar.text_input("Enter your email for daily updates")
if st.sidebar.button("Subscribe"):
    if email:
        save_email(email)
        st.sidebar.success("✅ Subscribed! You’ll receive daily updates.")
    else:
        st.sidebar.warning("⚠️ Please enter a valid email.")

# Main Page Title and Description
st.title("🗳️ NC Political News Tracker")
st.markdown("""
#### Get the latest news on North Carolina politics, featuring:
**Alma Adams**, **Don Davis**, **Mayor Vi Lyles**, and **Mayor Karen Bass**.
""")

# Display news articles for each selected politician
if selected_politicians:
    for person in selected_politicians:
        news_articles = get_news(person, keyword=keyword, limit=news_limit)
        if news_articles:
            st.markdown(f"## 📰 Latest News on {person}")
            for article in news_articles:
                col1, col2 = st.columns([1, 3])  # Left column for image, right for text
                with col1:
                    st.image(article["Image"], use_container_width=True)
                with col2:
                    st.markdown(f"### {article['Title']}")
                    st.markdown(f"🕒 {article['Published']}")
                    st.markdown(f"[🔗 Read More]({article['Link']})")
        else:
            st.warning(f"No recent news found for {person}.")
else:
    st.info("Please select at least one politician to see news.")
