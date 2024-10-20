import discord
import platform, os, sys, discord, asyncio
from discord.ext import commands
import discord
from discord import app_commands, Interaction, TextChannel
from helpers import load_json
from discord.app_commands import AppCommandError
import logging
logging.basicConfig(level=logging.DEBUG)

# Load configuration
config = load_json("config.json")

# Setup bot and command tree
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="b/", intents=intents)
tree = bot.tree
bot.logs = load_json("log.json")
bot.config = load_json("config.json")
# Event handler when bot is ready

@bot.event
async def on_ready():
    """Executed when the bot is ready."""
    activeservers = bot.guilds
    tree.clear_commands(guild=None)
    await load_cogs()
    await tree.sync(guild=None)
    for guild in activeservers:
        print(f"Syncing commands for guild {guild.name}")
        await tree.sync(guild=discord.Object(id=guild.id))
    print(f"Logged in as {bot.user.name} | discord.py v{discord.__version__} | Python {platform.python_version()} | {platform.system()} {platform.release()}")

# Load all cogs dynamically from the /cogs directory
async def load_cogs():
    cogs_directory = "cogs"
    
    # Iterate over files in the /cogs directory
    for filename in os.listdir(cogs_directory):
        # Check if the file starts with [cog] and ends with .py
        if filename.endswith(".py") and not filename.startswith("_"):
            cog_name = f"{cogs_directory}.{filename[:-3]}"  # Remove .py extension
            try:
                await bot.load_extension(cog_name)
                print(f"[SUCCESS] loaded {cog_name}")
            except Exception as e:
                print(f"[ERROR] Failed to load {cog_name}: {e}")


@bot.tree.error  
async def on_command_error(interaction: Interaction, error: Exception):
    """Handle errors raised during command execution."""
    if isinstance(error, AppCommandError):
        await interaction.response.send_message(f"Command error occurred: {str(error)}")
    else:
        await interaction.response.send_message(f"An unexpected error occurred: {str(error)}")

# Main function
if __name__ == "__main__":
    bot.run(config["token"])