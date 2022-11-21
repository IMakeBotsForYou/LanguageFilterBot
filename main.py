import platform
import sys
import discord

import asyncio
from discord.ext import tasks
import discord.ext.commands
from discord.ext.commands import Bot, Context
from helpers import *
from time import time, ctime

intents = discord.Intents.all()

bot = Bot(command_prefix=commands.when_mentioned_or(
    config["prefix"]), intents=intents, help_command=None)


bot.config = config
last_sent = {}

async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    print("\n")
    for file in os.listdir(f"./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")
    print("\n")


asyncio.run(load_cogs())


@bot.event
async def on_ready() -> None:
    """
    The code in this even is executed when the bot is ready
    """
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """

    #botのメッセージを無視
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)

    # jp_id = 928310346622599279
    # en_id = 946060955618517022
    # zatudan_id = 802123797791768587
    # general_id = 772882331744337936

    config = load_json("config.json")
    active_jp_filters = config["active_jp_filters"]
    active_en_filters = config["active_en_filters"]

    if message.channel.id not in active_jp_filters and message.channel.id not in active_en_filters:
        return
    #バカどもが「.」でスパムしてたから    
    # if message.content == "." or message.content == "\\.":
    #     await message.delete()

    if message.content.startswith("||") and message.content.endswith("||"):
        print(f"\nSpoiler message, ignoring!")
        return
    
    print("\n\n")


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
    if message.channel.id not in last_sent:
        last_sent[message.channel.id] = 0

    #############################
    #########  CHECKING #########
    #############################
    if message.channel.id in active_jp_filters:
        # Beginner JPのチャンネルで、英語と日本語の割合が設定された割合を超えたら消す
        #４文字以内は許される
        if en_ch < config["allowed_min_jp"]:
            return

        if english_percent > config["allowed_%_en"]:
            print(f"Deleting")
            if time()-last_sent[message.channel.id] > config["warning_message_time"]:
                embed = discord.Embed(
                    title="Shh!",
                    description=fr"This channel has a JP filter. To say something in english, use \|\|message\|\|",
                    color=0xCC11BB
                    )
                last_sent[message.channel.id] = time()
                await message.channel.send(embed=embed, delete_after=config["warning_message_time"])
            await message.delete()
            

    if message.channel.id in active_en_filters:
        # Beginner ENもまた然り
        #３文字以内は許される
        if jp_ch < config["allowed_min_en"]:
            return

        if japanese_percent > config["allowed_%_jp"]:
            print(f"Deleting")

            if time()-last_sent[message.channel.id]>config["warning_message_time"]:
                embed = discord.Embed(
                    title="しーッ！",
                    description=fr"このチャンネルには英語フィルターが掛けてあります。　日本語で一言を言いたい場合は、 \|\|こうやってメッセージを隠してください。\|\|",
                    color=0xCC11BB
                    )
                last_sent[message.channel.id] = time()
                await message.channel.send(embed=embed, delete_after=config["warning_message_time"])
            await message.delete()
            
            await asyncio.sleep(config["warning_message_time"])


# @bot.event
# async def on_command_error(context: Context, error) -> None:
#     """
#     The code in this event is executed every time a normal valid command catches an error
#     :param context: The context of the normal command that failed executing.
#     :param error: The error that has been faced.
#     """
#     msg = context.message
#     if isinstance(error, commands.CheckFailure):
#         print(f"{msg.author} tried running \"{msg.content}\"\nFailed.\n")

bot.run(config["token"])