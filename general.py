import discord
import psutil
import asyncio
import json
from discord.ext import commands

KEYWORDS_FILE = "keywords.json"
FEEDS_FILE = "feeds.json"

def load_keywords():
    with open(KEYWORDS_FILE) as f:
        return json.load(f)

def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)

def save_feeds(feeds):
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds, f)

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()

        if battery:
            charging = "charging" if battery.power_plugged else "discharging"
            battery_line = f"Battery: {battery.percent:.0f}% ({charging})"
        else:
            battery_line = "Battery: not available"

        msg = (
            f"**System Status**\n"
            f"CPU: {cpu}%\n"
            f"RAM: {ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB ({ram.percent}%)\n"
            f"Disk: {disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB ({disk.percent}%)\n"
            f"{battery_line}"
        )
        await ctx.send(msg)

    @commands.command()
    async def prune(self, ctx, amount: int = 100):
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"Deleted {len(deleted)} messages.")
        await asyncio.sleep(3)
        await msg.delete()

    # --- keyword commands ---

    @commands.command()
    async def keywords(self, ctx):
        keywords = load_keywords()
        if not keywords:
            await ctx.send("No keywords set.")
            return
        await ctx.send("**Active keywords:**\n" + "\n".join(f"• {kw}" for kw in keywords))

    @commands.command()
    async def addkeyword(self, ctx, *, keyword: str):
        keywords = load_keywords()
        if keyword in keywords:
            await ctx.send(f"`{keyword}` is already in the list.")
            return
        keywords.append(keyword)
        save_keywords(keywords)
        await ctx.send(f"✅ Added keyword `{keyword}`.")

    @commands.command()
    async def removekeyword(self, ctx, *, keyword: str):
        keywords = load_keywords()
        if keyword not in keywords:
            await ctx.send(f"`{keyword}` not found.")
            return
        keywords.remove(keyword)
        save_keywords(keywords)
        await ctx.send(f"🗑️ Removed keyword `{keyword}`.")

    # --- feed/source commands ---

    @commands.command()
    async def sources(self, ctx):
        feeds = load_feeds()
        if not feeds:
            await ctx.send("No sources set.")
            return
        await ctx.send("**Active sources:**\n" + "\n".join(f"• **{name}**: {url}" for name, url in feeds.items()))

    @commands.command()
    async def addsource(self, ctx, name: str, url: str):
        feeds = load_feeds()
        if name in feeds:
            await ctx.send(f"`{name}` already exists.")
            return
        feeds[name] = url
        save_feeds(feeds)
        await ctx.send(f"✅ Added source `{name}`.")

    @commands.command()
    async def removesource(self, ctx, *, name: str):
        feeds = load_feeds()
        if name not in feeds:
            await ctx.send(f"`{name}` not found.")
            return
        feeds.pop(name)
        save_feeds(feeds)
        await ctx.send(f"🗑️ Removed source `{name}`.")

    @commands.command()
    async def help(self, ctx):
        msg = (
            "**Available commands:**\n\n"
            "**System**\n"
            "• `!status` — CPU, RAM, disk and battery usage\n"
            "• `!prune [amount]` — delete messages (default 100)\n\n"
            "**Keywords**\n"
            "• `!keywords` — list active keywords\n"
            "• `!addkeyword <keyword>` — add a keyword\n"
            "• `!removekeyword <keyword>` — remove a keyword\n\n"
            "**Sources**\n"
            "• `!sources` — list active news sources\n"
            "• `!addsource <name> <url>` — add a news source\n"
            "• `!removesource <name>` — remove a news source\n\n"
            "**Other**\n"
            "• `!help` — show this message\n"
        )
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
