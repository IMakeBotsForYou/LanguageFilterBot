import os
import sys
import json
import discord
import asyncio
from discord import app_commands, Interaction, TextChannel
from discord.ext import commands, tasks
from discord.app_commands import Choice
from datetime import datetime, timedelta
from helpers import *


class General(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = load_json("config.json")


    @app_commands.command(name="reload", description="Restart the bot.")
    @is_owner()
    async def restart_bot(self, interaction: Interaction):
        """Restarts the bot by re-executing the main file."""
        await interaction.response.defer() 
        await interaction.followup.send("Restarting bot...")
        os.execv(sys.executable, ['py', 'main.py'])

    @app_commands.command(name="language_filter", description="Manage language filters for a channel.")
    @app_commands.describe(filter_type="Only allow a certain language in this channel.")
    @app_commands.choices(action = [Choice(name="Add filter", value="add"), Choice(name="Remove filter", value="remove")])
    @app_commands.choices(filter_type = [Choice(name="Only Allow English", value="en"), Choice(name="Only Allow Japanese", value="jp")])
    @is_owner()
    async def filter_command(self, interaction: Interaction, action: str, channel: TextChannel, filter_type: str):
        """Add or remove a language filter to a channel"""
        await interaction.response.defer() 
        self.config = load_json("config.json")
        path = f"active_{filter_type}_filters"
        if filter_type not in ['en', 'jp']:
            await interaction.followup.send(embed=simple_embed(
                title="Error", description="Filter must be 'en' or 'jp'.", color=0xFF55BB
            ))
            return
        if action == "add":
            if channel.id in self.config[path]:
                await interaction.followup.send(embed=simple_embed(
                    title="Error", description=f"{filter_type.upper()} filter already set in {channel.name}.", color=0xFF55BB
                ))
            else:
                self.config[path].append(channel.id)
                with open("config.json", "w") as f:
                    json.dump(self.config, f, indent=2)
                await interaction.followup.send(embed=simple_embed(
                    title="Success", description=f"Added {filter_type.upper()} filter to {channel.name}.", color=0x90FF99
                ))
        elif action == "remove":
            if channel.id in self.config[path]:
                with open("config.json", "w") as f:
                    json.dump(self.config, f, indent=2)
                await interaction.followup.send(embed=simple_embed(
                    title="Success", description=f"Removed {filter_type.upper()} filter from {channel.name}.", color=0x90FF99
                ))
            else:
                await interaction.followup.send(embed=simple_embed(
                    title="Error", description=f"{filter_type.upper()} filter not set in {channel.name}.", color=0xFF55BB
                ))

    @app_commands.command(name="ping", description="Check bot's latency.")
    @is_commands_channel()
    async def ping_command(self, interaction: Interaction):
        """Responds with the bot's current latency."""
        await interaction.response.defer() 
        latency = round(self.bot.latency * 1000)
        await interaction.followup.send(embed=simple_embed(
            title="🏓 Pong!", description=f"Bot latency is {latency}ms.", color=0x9C84EF
        ))

async def setup(bot):
    await bot.add_cog(General(bot))
