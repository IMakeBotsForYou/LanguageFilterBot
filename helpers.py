from re import compile, search
from typing import Callable, TypeVar
import os
import json
import discord
from time import ctime
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



def log(message: discord.Message, spacing="\n") -> None:
    print(spacing)
    # Filter through stuff that isn't actually characters
    content = message.content
    

    ##################################
    ######### KEEP TEXT ONLY #########
    ##################################
    fixed_content = find_emoji.sub('', content)
    fixed_content = find_links.sub('', fixed_content)
    fixed_content = find_characters.sub('', fixed_content)

    len_content = len(fixed_content)

    #############################################
    ######### FIND AMOUNT OF CHARACTERS #########
    #############################################
    doubleyous_search = search("[ｗw]+$", fixed_content)
    if doubleyous_search:
        ws = len(search("[ｗw]+$", fixed_content).group())
    else:
        ws = 0

    en_ch = len(find_english.findall(fixed_content)) - ws

    

    jp_ch = len(find_japanese.findall(fixed_content)) + ws

    len_content = 1 if len_content == 0 else len_content


    #############################################
    ######### FIND % OF CHARACTERS #########
    #############################################
    english_percent =   100 * en_ch / len_content
    japanese_percent =  100 * jp_ch / len_content
    # non_en_jp_percent = 1 - english_percent - japanese_percent
    # Remove weird characters from channel name
    channel_name = fix_channel_name(message.channel.name)
    

    ############################
    ######### PRINTING #########
    ############################
    print(f"Registered {message.author}'s message in {channel_name}: '{content}'")
    msg = f"Len: {len(content)}  EN_CH: {en_ch}   JP_CH: {jp_ch}\n"
    msg += f"JP%: {round(japanese_percent, 2)} EN%: {round(english_percent, 2)}\n"
    msg += ctime()
    print(msg)
    print(spacing)


# Decorators
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


