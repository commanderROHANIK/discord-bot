import discord
import psutil
import asyncio
from discord.ext import commands

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

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))