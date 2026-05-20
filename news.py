import discord
import feedparser
import json
import os
from discord.ext import commands, tasks

KEYWORDS_FILE = "keywords.json"
SEEN_FILE = "seen_articles.json"
NEWS_CHANNEL_NAME = "general"
FEEDS_FILE = "feeds.json"

def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)

def load_keywords():
    with open(KEYWORDS_FILE) as f:
        return json.load(f)

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

class NewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    @tasks.loop(minutes=30)
    async def check_news(self):
        seen = load_seen()
        first_run = len(seen) == 0
        channel = discord.utils.get(self.bot.get_all_channels(), name=NEWS_CHANNEL_NAME)
        if not channel:
            return

        keywords = load_keywords()
        
        for source, url in load_feeds().items():
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.link in seen:
                    continue
                title = entry.get("title", "")
                if first_run:
                    seen.add(entry.link)  # silently mark as seen
                elif any(kw.lower() in title.lower() for kw in keywords):
                    await channel.send(f"**[{source}]** {title}\n{entry.link}")
                    seen.add(entry.link)

        save_seen(seen)

    @check_news.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NewsCog(bot))