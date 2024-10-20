import os, sys, json
from discord.ext import commands
from helpers import *
from time import time
from datetime import datetime
import json

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sent = {}  # To track the last sent message per channel
        self.warning_message_time = bot.config["warning_message_time"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handles every message sent, applying language and user filters."""

        # Ignore messages from the bot itself, owners, or other bots
        # if message.author == self.bot.user or message.author.bot or message.author.id in self.bot.config["owners"]:
        if message.author == self.bot.user:
            return

        # Process bot commands in messages
        await self.bot.process_commands(message)

        # Special filter for a specific user
        if message.author.id == 961960226418991104 and "吸う" in message.content:
            await self.try_delete(message)

        # Handle Direct Messages
        if not message.guild:
            print(f"DM by: {message.author.name} @ {ctime()}: {message.content}")
            return

        # Skip staff channels based on category
        if message.channel.category and message.channel.category.name == "💗 Staff":
            return

        # Initialize channel's last sent message time if it doesn't exist
        if message.channel.id not in self.last_sent:
            self.last_sent[message.channel.id] = 0

        # Apply foreign language filtering
        await self.apply_foreign_language_filter(message)

        # Apply channel-specific language filters
        await self.apply_language_filters(message)

    async def apply_foreign_language_filter(self, message):
        """Checks if the message contains too much foreign language content and deletes it if needed."""
        _, _, _, _, foreign_percentage, language_chars = calculate_percentages(message)
        # Conditions for triggering foreign language filter warnings
        if (foreign_percentage > 0.2 and len(message.content) > 16) or (foreign_percentage > 0.5 and len(message.content) >= 3):
            if time() - self.last_sent[message.channel.id] > self.warning_message_time:
                embed = simple_embed(
                    title="What language is that? 何語ですか？",
                    description="This is an EN/JP server. Please respect the rules.\n日英サーバです。ルールに従ってください。",
                    color=0xCC11BB
                )
                await message.channel.send(embed=embed, delete_after=self.warning_message_time)
            print(f"Deleted message by {message.author.name}({message.author.id}):\n{message.content}")
            print("\n".join([f"{language}:\t{text}" for text, language in language_chars]))
            # Delete the message and update the last sent time for the channel
            await self.try_delete(message)
            self.last_sent[message.channel.id] = time()

    async def apply_language_filters(self, message):
        """Applies English and Japanese filters based on the channel-specific configuration."""
        en_filters = self.bot.config["active_en_filters"]
        jp_filters = self.bot.config["active_jp_filters"]

        # Calculate percentages of English and Japanese in the message
        en_ch, jp_ch, en_percent, jp_percent, foreign_percentage, _ = calculate_percentages(message)

        # Apply English filter on JP channels
        if message.channel.id in jp_filters and en_percent > self.bot.config["allowed_%_en"] and en_ch > self.bot.config["allowed_min_en"]:
            await self.delete_with_warning(
                message,
                title="Shh!",
                description="This channel has a JP filter. Use ||spoiler tags|| for English."
            )

        # Apply Japanese filter on EN channels
        elif message.channel.id in en_filters and jp_percent > self.bot.config["allowed_%_jp"] and jp_ch > self.bot.config["allowed_min_jp"]:
            await self.delete_with_warning(
                message,
                title="しーッ！",
                description="このチャンネルには英語フィルターが掛けてあります。"
            )

    def add_message_to_logs(self, message: discord.Message):
        user_string = f"{message.author.name}_{message.author.id}"
        deleted_object = {
                "channel": message.channel.name,
                "content": message.content,
                "timestamp": datetime.fromtimestamp(time()).strftime('%a %b %d %H:%M:%S %Y')
            }
        if user_string not in self.bot.logs["deleted"]:
            self.bot.logs["deleted"][user_string] = [deleted_object]
        else:
            self.bot.logs["deleted"][user_string].append(deleted_object)

        with open("log.json", "w") as f:
            json.dump(self.bot.logs, f, indent=2)

    async def try_delete(self, message: discord.Message):
        """Attempts to delete a message and handles exceptions."""
        try: 
            self.add_message_to_logs(message)
            await message.delete()
        except discord.errors.Forbidden:
            print(f"Failed to delete message in {message.channel} by {message.author.name}")
        except discord.errors.NotFound:
            print(f"Message \"{message.channel}\" by {message.author.name} not found. Probably deleted.")


    async def delete_with_warning(self, message: discord.Message, title: str, description: str):
        """Deletes a message and sends an embedded warning to the channel."""
        await self.try_delete(message)
        embed = simple_embed(title=title, description=description, color=0xFF0000)
        await message.channel.send(embed=embed, delete_after=self.warning_message_time)


# Setup function to add the Cog to the bot
async def setup(bot):
    await bot.add_cog(MessageHandler(bot))