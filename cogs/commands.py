import platform
import discord
import os
import subprocess
import json
import sys
from discord import app_commands, TextChannel
from discord.ext import commands
from discord.ext.commands import Context
from helpers import is_owner, is_commands_channel, load_json

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_json("config.json")
    
    @commands.hybrid_command(
        name="reload",
        description="Restart the bot.",
    )
    @is_owner()
    async def restart_bot(self, context) -> None:
        # 雑な再起動機能

        print("\n\n")
        print("||||||||||||||||||||||||||||||||")
        print("||||||||||| RESTART ||||||||||||")
        print("||||||||||||||||||||||||||||||||")
        print("\n\n")

        await context.message.add_reaction("👍")
        os.execv(sys.executable, ['py', 'main.py'])


    @commands.hybrid_command(
        name="filter",
        description="Check if the bot is alive.",
    )
    @is_owner()
    async def filter(self, context, action: str, channel: discord.TextChannel, filter_type: str) -> None:
        global config
        path = f"active_{filter_type}_filters"
        channel_id = channel.id

        config = load_json("config.json")
        if action == "add" and channel_id not in config[path]:
            config[path].append(channel_id)

        elif action == "remove":
            config[path].remove(channel_id)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)

        config = load_json("config.json")

        embed = discord.Embed(
            title="Success!",
            description=f"{'Added' if action == 'add' else 'Removed'} \
                          {filter_type} filter \
                          {'to' if action == 'add' else 'from'} \
                          {channel.name}!",
            color=0x90FF99
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )

    @is_commands_channel()
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.
        
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))