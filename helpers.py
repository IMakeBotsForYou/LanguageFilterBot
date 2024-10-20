import os
import sys
import json
import discord
from typing import Callable, TypeVar
from discord.ext import commands
from time import ctime
import emoji
import re

# Define custom types for decorators
T = TypeVar("T")

# Constants
KEEP_LOG = 100
LOG_FILE_PATH = "log.json"
LANGUAGE_PATTERNS = {
    "english": r"[a-zA-Z]+",
    "arabic": r"[\u0600-\u06FF]+",
    "persian": r"[\u0600-\u06FF\uFB8A-\uFBFE\uFE70-\uFEFF]+",
    "cyrillic": r"[\u0400-\u04FF]+",
    "greek": r"[\u0370-\u03FF]+",
    "hebrew": r"[\u0590-\u05FF]+",
    "bengali": r"[\u0980-\u09FF]+",
    "devanagari": r"[\u0900-\u097F]+",
    "tamil": r"[\u0B80-\u0BFF]+",
    "telugu": r"[\u0C00-\u0C7F]+",
    "gujarati": r"[\u0A80-\u0AFF]+",
    "kannada": r"[\u0C80-\u0CFF]+",
    "malayalam": r"[\u0D00-\u0D7F]+",
    "thai": r"[\u0E00-\u0E7F]+",
    "lao": r"[\u0E80-\u0EFF]+",
    "khmer": r"[\u1780-\u17FF]+",
    "myanmar": r"[\u1000-\u109F]+",
    "sinhala": r"[\u0D80-\u0DFF]+",
    "georgian": r"[\u10A0-\u10FF]+",
    "armenian": r"[\u0530-\u058F]+",
    "hangul": r"[\uAC00-\uD7AF]+",
    "japanese": r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]+",
    "chinese": r"[\u4DC0-\u9FFF]+",
    "tibetan": r"[\u0F00-\u0FFF]+",
    "mongolian": r"[\u1800-\u18AF]+"
}

# Compiling regex patterns
find_emoji = re.compile(r'<a?:\w+:\d+>|\U0001F000-\U0001FFFF')
find_characters = re.compile(r"[\U0001F600-\U0001F64F0-9?><;,.{}[\]\-+=~!@#$%\^&*|'、\\_ー¯/\n\s:\(\)．‥…´\"”“⁉！！？・ー、。]", flags=re.UNICODE)
find_links = re.compile(r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
find_spoilers = re.compile(r"\|\|.+?\|\|")
remove_demojized_emojis = re.compile(":.+?:")

# Combine language patterns
languages_pattern = re.compile("|".join(f"(?P<{lang}>{pattern})" for lang, pattern in LANGUAGE_PATTERNS.items()))


# Utility Functions
def load_json(filepath: str) -> dict:
    """Loads JSON data from a file."""
    if not os.path.isfile(filepath):
        sys.exit(f"{filepath} not found! Please add it and try again.")
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def simple_embed(title: str, description: str, color: int = 0xAABBBB, footer: str = "") -> discord.Embed:
    """Creates a simple Discord embed message."""
    embed = discord.Embed(title=title, description=description, color=color)
    if footer:
        embed.set_footer(text=footer)
    return embed


def run_filters(filters: list, text: str) -> str:
    """Applies a list of regex filters to clean the text from unwanted patterns."""
    for fl in filters:
        text = fl.sub("", text)
    text = text.replace(":", "\\!")
    text_decoded = emoji.demojize(text)
    text_cleaned = remove_demojized_emojis.sub("", text_decoded)
    text_cleaned = re.sub(r"w{2,}", "", text)

    return text_cleaned.replace("\\!", ":")


def clean(content: str) -> str:
    """Cleans content by removing emojis, spoilers, links, and special characters."""
    return run_filters([find_emoji, find_spoilers, find_links, find_characters], content)


def calculate_percentages(message: discord.Message) -> tuple:
    """Calculates the percentage of English and Japanese characters in the message content."""
    content = message.content
    fixed_content = clean(content)
    len_content = len(fixed_content)
    # Find matches for language patterns
    language_matches = languages_pattern.finditer(fixed_content)



    # Character counts
    language_chars = [(match.group(), match.lastgroup) for match in language_matches if match.lastgroup]

    foreign_chars = 0
    en_chars = 0 
    jp_chars = 0

    for group in language_chars:
        text, language = group
        amount = len(text)
        # Count 'w's in the message
        if language == "english":
            en_chars += amount
        elif language == "japanese":
            jp_chars += amount
        else:
            foreign_chars += amount

    len_content = max(1, len_content)  # Prevent division by zero

    # Calculate percentages
    english_percent =  en_chars / len_content
    japanese_percent = jp_chars / len_content
    foreign_percent =  foreign_chars / len_content
    return en_chars, jp_chars, english_percent, japanese_percent, foreign_percent, language_chars


def log_message(author: discord.User, channel_name: str, content: str, deleted: bool) -> None:
    """Logs the message in a JSON file."""
    name = author.name
    user_id = author.id
    if channel_name == "「mudae」":
        return

    # Create a log entry
    log_entry = {
        "channel": channel_name,
        "content": content,
        "timestamp": ctime()
    }

    # Load existing log data
    log_data = {}
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
            try:
                log_data = json.load(log_file)
            except json.JSONDecodeError:
                pass

    # Update the log
    deleted_or_not = "deleted" if deleted else "not_deleted"
    username_and_id = f"{name}_{user_id}"

    if deleted_or_not not in log_data:
        log_data[deleted_or_not] = {}

    if username_and_id not in log_data[deleted_or_not]:
        log_data[deleted_or_not][username_and_id] = []

    log_data[deleted_or_not][username_and_id].append(log_entry)

    # Write back the updated log
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as log_file:
        json.dump(log_data, log_file, indent=4, ensure_ascii=False)


# Decorators
def is_owner() -> Callable[[T], T]:
    """Custom decorator to check if the command executor is the bot owner."""
    async def predicate(ctx: commands.Context) -> bool:
        owners = load_json("config.json")["owners"]
        return ctx.message.author.id in owners
    return commands.check(predicate)


def is_commands_channel() -> Callable[[T], T]:
    """Custom decorator to check if the command is executed in a specific bot channel."""
    bot_channels = [778209104300212234, 785118485377974282, 1291049930114207754]
    async def predicate(ctx: commands.Context) -> bool:
        return ctx.channel.id in bot_channels
    return commands.check(predicate)


def convert_to_milliseconds(time_string):
    try:
        # Regex pattern to match the format
        pattern = r'(\d+)([dhms])'
        
        # Initialize total milliseconds
        total_milliseconds = 0
        
        # Match all occurrences in the string
        matches = re.findall(pattern, time_string)
        
        # Conversion factors
        conversion_factors = {
            'd': 24 * 60 * 60 * 1000,  # days to milliseconds
            'h': 60 * 60 * 1000,       # hours to milliseconds
            'm': 60 * 1000,            # minutes to milliseconds
            's': 1000                  # seconds to milliseconds 
        }
        
        # Calculate total milliseconds
        for value, unit in matches:
            total_milliseconds += int(value) * conversion_factors[unit]
        
        return total_milliseconds
    except Exception:
        return None