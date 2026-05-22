import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

    config = json.load(open("config.json"))
    for guild in bot.guilds:
        existing = [c.name for c in guild.channels]
        for key in ["news_channel", "alerts_channel"]:
            name = config[key]
            if name not in existing:
                await guild.create_text_channel(name)
                print(f"Created #{name}")

    await bot.load_extension("general")
    await bot.load_extension("news")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

token = os.getenv("DISCORD_TOKEN")
bot.run(token)