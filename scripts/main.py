import json
import feedparser
from openai import OpenAI
from telegram import Bot
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load config
with open('config.json') as f:
    config = json.load(f)

INTERESTS = config['interests']
SOURCES = config['sources']

# Get API keys from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI and Telegram Bot
client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)

def fetch_rss_articles(sources, limit=20):
    """
    Fetch recent articles from RSS feeds.
    """
    articles = []
    for src in sources:
        feed = feedparser.parse(src)
        for entry in feed.entries[:limit]:
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', '')
            })
    return articles

def create_digest(articles, interests):
    """
    Ask ChatGPT to filter + summarise + format into digest.
    """
    text = "\n\n".join(
        [f"Title: {a['title']}\nSummary: {a['summary']}" for a in articles]
    )

    prompt = f"""
    You are a helpful assistant that creates a daily personalised news digest.
    User interests: {', '.join(interests)}

    Here are some recent articles:

    {text}

    Include only articles relevant to the user's interests.
    Summarise key facts, figures, or newsworthy points in 2–3 concise sentences.
    
    Please format the digest as a plain text bulleted list of articles. For each article:
    - Start with a bullet point (e.g., '- ')
    - Provide a title.
    - On the next line, provide a concise summary.
    - Do not include any links or styling.
    - Select a maximum of 8 relevant articles.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content

async def send_digest(digest):
    """
    Send the digest to the user via Telegram.
    """
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=digest)

async def main():
    articles = fetch_rss_articles(SOURCES)
    digest = create_digest(articles, INTERESTS)
    await send_digest(digest)
    print("Digest sent!")

if __name__ == "__main__":
    asyncio.run(main())