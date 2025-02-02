import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define Google News RSS feeds for each politician
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina"
}

def get_news(person, keyword="", limit=5):
    """Fetch the top news articles for the given person from Google News RSS, with optional keyword filtering."""
    feed_url = URLS.get(person)
    if not feed_url:
        return []
    
    response = requests.get(feed_url)
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
            "Published": item.pubDate.text
        })
    
    return articles

# Streamlit UI Configuration
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
        body { 
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
        }
        .news-container {
            padding: 20px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .news-title {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }
        .news-meta {
            font-size: 14px;
            color: #7f8c8d;
        }
        .news-link {
            font-size: 16px;
            color: #2980b9;
            font-weight: bold;
            text-decoration: none;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: bold;
            color: #34495e;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            background-color: #3498db;
            color: white;
            padding: 10px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #2980b9;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown('<p class="sidebar-title">🔍 Filter News</p>', unsafe_allow_html=True)
selected_politicians = st.sidebar.multiselect(
    "Select Politician(s)", list(URLS.keys()), default=list(URLS.keys())
)
keyword = st.sidebar.text_input("Search for a topic (optional):")
news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

# Main Page Title
st.title("🗳️ NC Political News Tracker")
st.markdown("#### Get the latest news on North Carolina politics, featuring **Alma Adams** and **Don Davis**.")

# Display News in Sections
if selected_politicians:
    for person in selected_politicians:
        news_articles = get_news(person, keyword=keyword, limit=news_limit)
        
        if news_articles:
            st.markdown(f"## 📰 Latest News on {person}")
            cols = st.columns(2)  # Use two columns for news layout
            
            for i, article in enumerate(news_articles):
                with cols[i % 2]:  # Alternate between columns
                    st.markdown('<div class="news-container">', unsafe_allow_html=True)
                    st.markdown(f'<p class="news-title">{article["Title"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="news-meta">Published: {article["Published"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<a class="news-link" href="{article["Link"]}" target="_blank">Read More</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"No recent news found for {person}.")
else:
    st.info("Please select at least one politician to see news.")

