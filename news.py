import discord
import feedparser
import json
import os
from discord.ext import commands, tasks

KEYWORDS_FILE = "keywords.json"
SEEN_FILE = "seen_articles.json"
FEEDS_FILE = "feeds.json"
CONFIG_FILE = "config.json"

def load_keywords():
    with open(KEYWORDS_FILE) as f:
        return json.load(f)

def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

class NewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        interval = load_config().get("check_interval_minutes", 15)
        self.check_news.change_interval(minutes=interval)
        self.check_news.start()

    def cog_unload(self):
        self.check_news.cancel()

    @tasks.loop(minutes=15)  # overridden in __init__ from config.json
    async def check_news(self):
        seen = load_seen()
        first_run = len(seen) == 0
        config = load_config()
        channel = discord.utils.get(self.bot.get_all_channels(), name=config["news_channel"])
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
                    seen.add(entry.link)
                elif any(kw.lower() in title.lower() for kw in keywords):
                    await channel.send(f"**[{source}]** {title}\n{entry.link}")
                    seen.add(entry.link)

        save_seen(seen)

    @check_news.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def setcheckinterval(self, ctx, minutes: int):
        if minutes < 1:
            await ctx.send("Interval must be at least 1 minute.")
            return
        config = load_config()
        config["check_interval_minutes"] = minutes
        save_config(config)
        self.check_news.cancel()
        self.check_news.change_interval(minutes=minutes)
        self.check_news.start()
        await ctx.send(f"✅ News check interval set to {minutes} minutes.")

async def setup(bot):
    await bot.add_cog(NewsCog(bot))