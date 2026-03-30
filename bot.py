import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is not set in the .env file")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# Load cogs
# -----------------------------
@bot.event
async def setup_hook():
    await bot.load_extension("cogs.card_cog")
    await bot.load_extension("cogs.commands.openpack")
    await bot.load_extension("cogs.commands.collection")
    await bot.load_extension("cogs.commands.activepack")
    await bot.load_extension("cogs.commands.changepack")
    await bot.load_extension("cogs.commands.viewpacks")
    await bot.load_extension("cogs.commands.give")
    await bot.load_extension("cogs.commands.stats")
    await bot.load_extension("cogs.commands.trade")
    await bot.load_extension("cogs.commands.cardinfo")
    await bot.load_extension("cogs.commands.commandslist")
    await bot.load_extension("cogs.commands.lottery")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# Run the bot like you wanted
bot.run(TOKEN)
