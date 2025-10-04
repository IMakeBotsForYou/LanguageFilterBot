import os
import sys
import json
import discord
import asyncio
from discord import app_commands, Interaction, TextChannel, Embed
from discord.ext import commands, tasks
from discord.app_commands import Choice
from datetime import datetime, timedelta
from helpers import *
import time
import uuid

def generate_unique_reminder_id():
    """Generate a unique reminder ID using UUID."""
    return uuid.uuid4().hex.replace("-", "")  # Generate a random unique ID


class Reminder(commands.Cog):
    group = app_commands.Group(name="reminder", description="Reminder Commands")

    def __init__(self, bot):
        self.bot = bot
        self.reminders_json_path = "reminders.json"
        self.reminders = self.load_reminders()  
        self.reminder_loop.start()

    def load_reminders(self):
        """Load reminders from reminders.json."""
        if os.path.exists(self.reminders_json_path):
            print("[SUCCESS] reminders.json loaded")
            with open(self.reminders_json_path, "r") as f:
                return json.load(f)
        else:
            print("[ERROR] reminders.json not found")
        return {}

    def save_reminders(self):
        """Save reminders to reminders.json."""
        with open(self.reminders_json_path, "w") as f:
            json.dump(self.reminders, f, indent=2)

    @group.command(name="add", description="Add a new reminder.")
    @app_commands.describe(time_from_now='Time from now (e.g. 1h5m)')
    async def add_reminder(self, interaction: Interaction, time_from_now: str, text: str, interval: str = None):
        """Add a new reminder for a specific time."""
        await interaction.response.defer()

        # Parse time and optional interval
        time_in_ms = convert_to_milliseconds(time_from_now)
        repeat_interval = convert_to_milliseconds(interval) if interval else None

        if time_in_ms is None:
            await interaction.followup.send(embed=Embed(
                title="Error", description="Invalid time format. Use '1m', '1h', etc.", color=0xFF5555
            ))
            return
        if repeat_interval is not None:
            if repeat_interval < convert_to_milliseconds("1m"):
                await interaction.followup.send(embed=Embed(
                    title="Error", description="Cannot repeat more than once a minute.", color=0xFF5555
                ))
                return

        # Generate a unique reminder ID
        reminder_id = generate_unique_reminder_id()

        user_id = str(interaction.user.id)
        current_timestamp = int(time.time() * 1000)
        reminder_time = current_timestamp + time_in_ms

        if user_id not in self.reminders:
            self.reminders[user_id] = []

        self.reminders[user_id].append({
            "id": reminder_id,
            "time": reminder_time,
            "repeat": bool(interval),  # Repeats if interval is provided
            "interval": repeat_interval,
            "channel_id": interaction.channel_id,
            "text": text
        })

        self.save_reminders()

        next_time_str = datetime.fromtimestamp(reminder_time / 1000).strftime('%Y-%m-%d %H:%M')

        await interaction.followup.send(embed=Embed(
            title="Success", description=f"Reminder set for **{next_time_str}** with ID **{reminder_id}**. Repeating: {'Yes' if interval else 'No'}.", color=0x55FF55
        ))

    @group.command(name="edit", description="Edit an existing reminder by its ID.")
    @app_commands.describe(reminder_id='Reminder ID')
    async def edit_reminder(self, interaction: Interaction, reminder_id: str, repeat: bool = None, interval: str = None):
        """Edit an existing reminder's repeat status or interval."""
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        if user_id not in self.reminders:
            await interaction.followup.send(embed=Embed(
                title="Error", description="You don't have any reminders.", color=0xFF5555
            ))
            return

        reminder = next((r for r in self.reminders[user_id] if r["id"] == reminder_id), None)
        if not reminder:
            await interaction.followup.send(embed=Embed(
                title="Error", description=f"No reminder found with ID **{reminder_id}**.", color=0xFF5555
            ))
            return

        if repeat is not None:
            reminder["repeat"] = repeat

        if interval:
            repeat_interval = convert_to_milliseconds(interval)
            if repeat_interval is None:
                await interaction.followup.send(embed=Embed(
                    title="Error", description="Invalid interval format. Use '1m', '1h', etc.", color=0xFF5555
                ))
                return
            reminder["interval"] = repeat_interval

        self.save_reminders()

        await interaction.followup.send(embed=Embed(
            title="Success", description=f"Reminder **{reminder_id}** updated.", color=0x55FF55
        ))

    @group.command(name="remove", description="Remove a reminder by its ID.")
    @app_commands.describe(reminder_id='Reminder ID')
    async def remove_reminder(self, interaction: Interaction, reminder_id: str):
        """Remove an existing reminder by its ID."""
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        if user_id not in self.reminders:
            await interaction.followup.send(embed=Embed(
                title="Error", description="You don't have any reminders.", color=0xFF5555
            ))
            return

        reminders = self.reminders[user_id]
        reminder = next((r for r in reminders if r["id"] == reminder_id), None)
        if not reminder:
            await interaction.followup.send(embed=Embed(
                title="Error", description=f"No reminder found with ID **{reminder_id}**.", color=0xFF5555
            ))
            return

        reminders.remove(reminder)
        self.save_reminders()

        await interaction.followup.send(embed=Embed(
            title="Success", description=f"Reminder **{reminder_id}** removed.", color=0x55FF55
        ))

    @group.command(name="list", description="List all your reminders.")
    async def list_reminders(self, interaction: Interaction):
        """List all reminders for the user."""
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        if user_id not in self.reminders or not self.reminders[user_id]:
            await interaction.followup.send(embed=Embed(
                title="Reminders", description="You don't have any active reminders.", color=0xFFFF55
            ))
            return

        embed = Embed(title="Your Reminders", color=0x55FFFF)
        for reminder in self.reminders[user_id]:
            next_time_str = datetime.fromtimestamp(reminder["time"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            embed.add_field(
                name=f"ID: {reminder['id']}",
                value=f"Time: {next_time_str}\nRepeat: {'Yes' if reminder['repeat'] else 'No'}\nText: {reminder['text']}",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @tasks.loop(seconds=60)
    async def reminder_loop(self):
        """Background task to check and send reminders."""
        current_time = int(time.time() * 1000)
        for user_id, reminders in self.reminders.items():
            for reminder in reminders:
                if reminder["time"] <= current_time:
                    channel = self.bot.get_channel(reminder["channel_id"])
                    user = self.bot.get_user(int(user_id))

                    next_time_str = ""

                    if reminder["repeat"]:
                        reminder["time"] = current_time + reminder["interval"]
                        next_time_str = "Next reminder at: " + str(datetime.fromtimestamp(reminder["time"] / 1000).strftime('%Y-%m-%d %H:%M'))
                    
                    if channel and user:
                        await channel.send(f"{user.mention}, {reminder['text']} {next_time_str}")
                    else:
                        reminders.remove(reminder)

                    if not reminder["repeat"]:
                        reminders.remove(reminder)


        self.save_reminders()


async def setup(bot):
    await bot.add_cog(Reminder(bot))
    # bot.tree.add_command(Reminder.group)
