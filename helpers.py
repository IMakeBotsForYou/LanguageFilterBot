from re import compile, search
from typing import Callable, TypeVar
import os
import json
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

# ディスコードでは、絵文字は 「 <a:名前:ID 」 もしくは 「 <:名前:ID 」
# のように表示される。　GIFの場合はAnimationのAがつく
find_emoji = compile(r'(?:<a:)|(?:<:)\w+:\d+>')
# 英語のアルファベット
find_english = compile(r"[a-zA-Z]")
# 日本語のひらがな、カタカナ、半角カタカナ、特別キャラクター、そして漢字
find_japanese = compile(r"[あ-んア-ン぀-ゟ゠-ヿ＀-￯]")
# 日本語と英語をあわせたフィルター
find_english_japanese = compile(r"[a-zA-Zあ-んア-ン぀-ゟ゠-ヿ＀-￯]")
# 特別キャラクター
find_characters = compile(r"[0-9?><;,.{}[\]\-_+=!@#$%\^&*|'、ー　-〿 ]")
# リンクのフィルター。　http, あるいは https のあとにどんな文字が付こうが入る
find_links = compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

def fix_channel_name(channel_name: str) -> str:
    # all_ch = find_english_japanese.findall(channel_name)
    # return "".join(all_ch)
    return channel_name[1:]

def get_channel_id(channel_name: str) -> str:
    # Gets something like #general and makes it #general
    return channel[2:-1] #  <#ID>

def load_json(json_path: str) -> json:
    if not os.path.isfile(json_path):
        sys.exit(f"{json_path}' not found! Please add it and try again.")
    else:
        with open(json_path) as file:
            return json.load(file)



config = load_json("config.json")
owners = config["owners"]

T = TypeVar("T")

def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is the owner.
    """
    async def predicate(context: commands.Context) -> bool:
        if context.message.author.id in owners:
            return True
        return False

    return commands.check(predicate)


def is_commands_channel() -> Callable[[T], T]:
    """
    This is a custom check to see if the channel the command is executed in is the bot channel
    """
    bot_channels = [778209104300212234, 785118485377974282]

    async def predicate(context: commands.Context) -> bool:
        print(fix_channel_name(context.channel.name))
        if context.channel.id in bot_channels:
            return True
        return False

    return commands.check(predicate)

