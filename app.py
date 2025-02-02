import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Define Google News RSS feeds for each politician
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina"
}

DEFAULT_IMAGE = "https://via.placeholder.com/150/3498db/ffffff?text=News"  # Default thumbnail

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
        link = item.link.text
        
        # Apply keyword filter if provided
        if keyword and keyword.lower() not in title.lower():
            continue

        articles.append({
            "Title": title,
            "Link": link,
            "Published": item.pubDate.text,
            "Image": DEFAULT_IMAGE  # Assign default image
        })
    
    return articles

# Function to save emails
def save_email(email):
    """Save email to CSV for future newsletters."""
    with open("subscribers.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email])
    return True

# Streamlit UI Configuration
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Custom CSS for better styling and readability
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
        .news-image {
            width: 120px;
            height: 120px;
            border-radius: 8px;
            margin-right: 15px;
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
        .email-box {
            padding: 15px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
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

# Email Subscription Section
st.sidebar.markdown('<p class="sidebar-title">📩 Subscribe for Daily News</p>', unsafe_allow_html=True)
email = st.sidebar.text_input("Enter your email for daily updates")
if st.sidebar.button("Subscribe"):
    if email:
        save_email(email)
        st.sidebar.success("✅ Subscribed! You’ll receive daily updates.")
    else:
        st.sidebar.warning("⚠️ Please enter a valid email.")

# Main Page Title
st.title("🗳️ NC Political News Tracker")
st.markdown("#### Get the latest news on North Carolina politics, featuring **Alma Adams** and **Don Davis**.")

# Display News in Sections
if selected_politicians:
    for person in selected_politicians:
        news_articles = get_news(person, keyword=keyword, limit=news_limit)
        
        if news_articles:
            st.markdown(f"## 📰 Latest News on {person}")
            
            for article in news_articles:
                st.markdown('<div class="news-container">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])  # Image on left, text on right
                with col1:
                    st.image(article["Image"], use_container_width=True)  # ✅ Fixed Deprecation Warning
                with col2:
                    st.markdown(f'<p class="news-title">{article["Title"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="news-meta">Published: {article["Published"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<a class="news-link" href="{article["Link"]}" target="_blank">Read More</a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"No recent news found for {person}.")
else:
    st.info("Please select at least one politician to see news.")
