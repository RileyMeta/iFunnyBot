# -*- coding: utf-8 -*-
"""
iFunnyBot
==============

An iFunny Embed bot

A bot that handles grabbing the info and embedding the memes from iFunny in Discord.

Author: Riley Ava
Created: 23/11/2026
Last Modified: 23/11/2026
Version: 1.0.0
License: GPL 3.0+
Repository: https://github.com/RileyMeta/iFunnyBot

Requirements:
    - Python 3.10 (or newer)

Usage:
    main [option] FILE...

Copyright (c) 2026 Riley Ava
"""
from dotenv import dotenv_values
from bs4 import BeautifulSoup
import datetime
import requests
import discord

################################################################################
# Global Variables
################################################################################
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}

################################################################################
# Actual Program
################################################################################
def parse_url(ifunny_url):
    """Get the information for the source of the meme

    Params:
        ifunny_url (str): The URL for the ifunny meme you wish to embed

    Returns:
        dict: The src info for the image or video of the meme
        None: If there is an error it will raise the error and return nothing.
    """
    if not ifunny_url.startswith("https://ifunny.co/"):
        raise ValueError(f"{ifunny_url} is not a url from iFunny")
        return None

    path_type = ifunny_url.rsplit("/", 2)[1]

    path = None
    element = None
    if path_type == "picture":
        class_name = "IqZk"
        element = "img"
        src_name = "src"

    elif path_type == "video":
        class_name = "h9wP"
        element = "video"
        src_name = "data-poster"

    else:
        raise ValueError(f"{ifunny_url} does not contain the required path contents.")
        return None

    response = requests.get(ifunny_url, headers=headers)
    if response.status_code != 200:
        raise ValueError("Unable to load webpage. Please double-check the URL.")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    author_name = soup.find("span", class_="R2rF").get_text().strip()
    author_pfp  = soup.find("img", class_="MmRx")["data-src"]
    upload_time = soup.find("div", class_="DvkZ").get_text()

    name_info = soup.find("h1", class_="yRZM")
    meme_name = None
    if name_info is not None:
        meme_name = name_info.get_text().strip()

    meme_src  = soup.find(element, class_=class_name)[src_name]

    return {
        "author_name": author_name,
        "author_pfp": author_pfp,
        "upload_time": upload_time,
        "meme_name": meme_name,
        "meme_src": meme_src,
        "meme_type": path_type,
    }

def create_embed(message):
    meme_info = parse_url(message)
    color = "#0c0c14"

    full_name = meme_info.get("meme_name")
    if full_name:
        meme_name = full_name[:100]
    else:
        meme_name = ""

    embed = discord.Embed(
        title=meme_name,
        description=full_name,
        url=message,
        color=discord.Color.from_rgb(12, 12, 20),
        timestamp=datetime.datetime.now()
    )
    if meme_info.get("meme_type") == "video":
        embed.add_field(name="This is a video", value="Please click it to watch")

    embed.set_author(name="iFunny", url=message, icon_url="https://m.media-amazon.com/images/I/41Yv6VC-fdL.png")
    embed.set_image(url=meme_info.get("meme_src"))
    embed.set_footer(text=meme_info.get("author_name"),
        icon_url=meme_info.get("author_pfp"))

    return embed

@client.event
async def on_ready():
    print(f"Online with name {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("https://ifunny.co/"):
        await message.channel.send(embed=create_embed(message.content))

if __name__ == "__main__":
    config = dotenv_values(".env")
    token = dotenv_values(".env").get("API_TOKEN", None)
    client.run(token)
