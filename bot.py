from pydoc import cli
import wave
import nextcord, asyncio, nextwave
from nextcord.ext import commands, ipc, tasks
from nextwave.ext import spotify
import requests
import openai
import requests
from requests.structures import CaseInsensitiveDict
import os
import google.oauth2.credentials
from googleapiclient.discovery import build
import config
import sqlite3
from sqlite3 import Error
import json
import time
import datetime

intents = nextcord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="b-", intents=intents)


@client.event
async def on_ready():
    print("Bot Is Online")
    #await check_twitch()
    #await check_for_new_videos()

async def add_channels():
    '''for channel_id in channel_ids:
        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel, 'youtube_id'))
        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel, 'youtube_id'))
        c.execute('SELECT youtube_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
        existing_channel = c.fetchone()
        if existing_channel:
            print(f"{channel_id} already added, skipping")
            continue
        else:
            c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (channel_id,))
            conn.commit()
            print(f"Added {channel_id}")'''
    
#async def on_ready():
#    print("Bot Is Online")
#    for channel_id in channel_ids:
#        youtbe_channel = c.execute('SELECT youtube_channel_id FROM discord_youtube')
#        if channel_id in youtbe_channel:
#            continue
#        else:
#            c.execute('UPDATE discord_youtube SET youtube_channel_id = ?', (channel_id,))
#            conn.commit()
#    check_for_new_videos.start()
    #client.loop.create_task(node_connect())

# Set up the YouTube Data API client
youtube = build('youtube', 'v3', developerKey=config.YOUTUBEKEY)
DISCORD_CHANNEL_ID = discord_channel

#@client.command()
#async def channel(ctx):
#    set(CHANNEL_ID = {ctx.message.content}) 
    
#channel_ids = []

#discord_ids = []

twitch_channelss = ['72702', 'AlpineVR']


@tasks.loop(minutes=1)
async def check_twitch():
    # Replace with your client ID and secret
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET
    
    # Connect to database
    con1 = sqlite3.connect('discord_twitch.db')
    c1 = con1.cursor()
    c1.execute('''CREATE TABLE IF NOT EXISTS discord_twitch
                (server_name, discord_channel_id integer, twitch_channel_id text, is_live interger, failed_last_send text)''')
    con1.commit()
    # Get list of channels from database
    ccursor = con1.execute("SELECT twitch_channel_id, is_live FROM discord_twitch")
    channel_info = ccursor.fetchall()
    
    with open('twitch_channels.txt', 'r') as f:
        channels_from_file = set(f.read().split())

    # Add any missing channels to the database
    for channel_name in channels_from_file:
        if not any(channel_name == row[0] for row in channel_info):
            print(f"Adding Channel {channel_name}")
            c1.execute("INSERT INTO discord_twitch VALUES (?, ?, ?, ?, ?)", ("", 0, channel_name, 0, ""))
            con1.commit()
    # Get access token with client ID and secret
    url = 'https://id.twitch.tv/oauth2/token'
    headd = CaseInsensitiveDict()
    headd["Content-Type"] = "application/x-www-form-urlencoded"
    dat = f"client_id={config.CLIENT_ID}&client_secret={config.CLIENT_SECRET}&grant_type=client_credentials&scope=channel%3Aread%3Asubscriptions"
    response = requests.post(url, headers=headd, data=dat)
    if response.status_code != 200:
        print(f"Error getting access token: {response.text}")
        return
    data = json.loads(response.text)
    access_token = data['access_token']
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
    }
    # Iterate over the channels and make API calls to get channel and stream information
    for channel in channel_info:
        channel_name = channel[0]
        is_live = channel[1]
        req_url = f'https://api.twitch.tv/helix/search/channels?query={channel_name}'
        req_response = requests.get(req_url, headers=headers)
        if req_response.status_code != 200:
            print(f"Error getting channel info for {channel_name}: {response.text}")
            continue
        req_data = json.loads(req_response.text)
        time.sleep(2)
        if req_data['data']:
            try:
                channel_isLive1 = req_data['data'][9]['is_live']
                channel_isLive1
                if channel_isLive1 == True:
                    game_name_fake = req_data['data'][9]['game_name']
                    user_name_fake = req_data['data'][9]['display_name']
                    title_fake_fake = req_data['data'][9]['title']
                    if not is_live:
                            # Update is_live column to True
                            con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                            con1.commit()
                            cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                            discord_info = cccursor.fetchone()
                            if discord_info == 0:
                                    # Post video in Discord channel
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_fake} Is Live Playing {game_name_fake}! {title_fake_fake} https://twitch.tv/{channel_name}")
                            else:
                                    time.sleep(2)
                    else:
                            continue
                else:
                    continue
            except IndexError:
                try:
                    channel_isLive = req_data['data'][1]['is_live']
                    channel_isLive
                    if channel_isLive == True:
                        game_name = req_data['data'][1]['game_name']
                        user_name = req_data['data'][1]['display_name']
                        title_fake = req_data['data'][1]['title']
                        if not is_live:
                                if not is_live:
                                    # Update is_live column to True
                                    con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                    con1.commit()
                                    cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                    discord_info = cccursor.fetchone()
                                    if discord_info == 0:
                                        # Post video in Discord channel
                                        channel = client.get_channel(discord_info)
                                        await channel.send(f"{user_name} Is Live Playing {game_name}! {title_fake} https://twitch.tv/{channel_name}")
                                    else:
                                        time.sleep(2)
                        else:
                                continue
                    else:
                        continue
                except IndexError:
                    try:
                            title = req_data['data'][1]['title']
                            title
                            con1.execute(f"UPDATE discord_twitch SET is_live = 0 WHERE twitch_channel_id = '{channel_name}'")
                            con1.commit()
                    except IndexError:
                            game_name_real = req_data['data'][0]['game_name']
                            user_name_real = req_data['data'][0]['display_name']
                            title_real = req_data['data'][0]['title']
                            if not is_live:
                                # Update is_live column to True
                                con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                con1.commit()
                                cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                discord_info = cccursor.fetchone()
                                if discord_info == 0:
                                    # Post video in Discord channel
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_real} Is Live Playing {game_name_real}! {title_real} https://twitch.tv/{channel_name}")
                                else:
                                    time.sleep(2)
                            else:
                                continue



conn = sqlite3.connect('discord_youtube.db')

c = conn.cursor()
    # Create a table with columns discord_channel_id, youtube_channel_id, and latest_video_id
c.execute('''CREATE TABLE IF NOT EXISTS discord_youtube
                (server_name, discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text)''')
conn.commit()


@tasks.loop(minutes=1)
async def update_db():
    with open('youtube.txt', 'r') as f:
        ids = f.readlines()
        for channel_id in ids:
            c.execute('SELECT youtube_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
            existing_channel = c.fetchone()
            if existing_channel:
                print(f"{channel_id} already added, skipping")
                continue
            else:
                c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (channel_id,))
                conn.commit()
                print(f"Added {channel_id}")
                continue
@tasks.loop(minutes=1)
async def update_db1():
    with open('discord.txt', 'r') as f:
        ids2 = f.readlines()
        for discord_id in ids2:
            c.execute('SELECT discord_channel_id FROM discord_youtube WHERE discord_channel_id = ?', (discord_id,))
            existing_channel = c.fetchone()
            if existing_channel:
                print(f"{discord_id} already added, skipping")
                continue
            else:
                c.execute('INSERT INTO discord_youtube (discord_channel_id) VALUES (?)', (discord_id,))
                conn.commit()
                print(f"Added {discord_id}")
                continue


# Define a task to run periodically to check for new videos
@tasks.loop(minutes=1)
async def check_for_new_videosa():
    '''for channel_id in channel_ids:
        print(f"Searching For Videos On {channel_id}")
        search_response = youtube.search().list(
            channelId=channel_id,
            type='video',
            part='id, snippet',
            order='date',
            maxResults=1
        ).execute()
        c.execute('SELECT latest_video_id FROM discord_youtube')
        previous_video_ids = [row[0] for row in c.fetchall()]
        if search_response['items']:
            latest_video_id = search_response['items'][0]['id']['videoId']
            channel_name = search_response['items'][0]['snippet']['channelTitle']
            if latest_video_id in previous_video_ids:
                print("No New Videos")
            else:
                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, channel_id))
                conn.commit()
                channel = client.get_channel(DISCORD_CHANNEL_ID)
                await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
        else:
            print("No new videos found.")'''

@tasks.loop(minutes=1)
async def check_for_new_videos():
    with open('youtube.txt', 'r') as f:
        yt_ids = f.readlines()
        for yt_channel_id in yt_ids:
            yt_channel_id = yt_channel_id.strip()
            print(yt_channel_id)
            c.execute('SELECT id, youtube_channel_id, discord_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (yt_channel_id,))
            existing_channel = c.fetchone()
            if existing_channel:
                print(f"{yt_channel_id} already added, skipping")
                row_id, exsisting_youtube_channel_id, existing_discord_channel_id = existing_channel
                if existing_discord_channel_id:
                    print(f"Discord ID already set for {yt_channel_id}, skipping")
                    continue
            else:
                c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (yt_channel_id,))
                conn.commit()
                print(f"Added {yt_channel_id}")
                row_id = c.lastrowid

            with open('discord.txt', 'r') as f:
                discord_ids = f.readlines()
                for discord_channel_id in discord_ids:
                    discord_channel_id = discord_channel_id.strip()
                    if existing_discord_channel_id == discord_channel_id:
                        print(f"Discord ID already set for {yt_channel_id}, skipping")
                        continue
                    else:
                        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE row = ?', (discord_channel_id, row_id,))
                        conn.commit()
                        print(f"Added {discord_channel_id} for {yt_channel_id}")
    cursorr = conn.execute("SELECT youtube_channel_id FROM discord_youtube")
    channel_ids = cursorr.fetchall()
    for yt_channel_id in channel_ids:
        print(f"Searching For Videos On {yt_channel_id}")
        search_response = youtube.search().list(
            channelId=yt_channel_id,
            type='video',
            part='id,snippet',
            order='date',
            maxResults=1
        ).execute()
        
        # Extract channel name and latest video ID from search response
        if search_response['items']:
            latest_video_id = search_response['items'][0]['id']['videoId']
            channel_name = search_response['items'][0]['snippet']['channelTitle']
        else:
            print("No new videos found.")
            continue
        
        # Check if latest video ID is different from previous video ID for this channel
        c.execute('SELECT latest_video_id, discord_channel_id, failed_last_send FROM discord_youtube WHERE youtube_channel_id = ?', (yt_channel_id,))
        row = c.fetchone()
        if row is not None:
            previous_video_id, discord_channel_id, failed_last_send = row
            if latest_video_id != previous_video_id:
                # Update latest video ID in the database
                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, yt_channel_id))
                conn.commit()
                if discord_channel_id:
                    # Post video in Discord channel
                    channel = client.get_channel(discord_channel_id)
                    if discord_channel_id != 0:
                        await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', yt_channel_id))
                        conn.commit()
                        print(f"New video posted in Discord channel {discord_channel_id}")
                    else:
                        print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', yt_channel_id))
                        conn.commit()
                else:
                    print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', yt_channel_id))
                    conn.commit()
            else:
                if failed_last_send == 'True':
                    channel1 = client.get_channel(discord_channel_id)
                    if discord_channel_id is not None and not 0:
                        await channel1.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', yt_channel_id))
                        conn.commit()
                    else:
                        print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                else:
                    print("No new videos")
        else:
            print(f"No entry found in database for YouTube channel {yt_channel_id}")



# Define a command to manually check for new videos
@client.command()
async def videos(ctx):
    await ctx.send("Checking For Videos!")
    check_for_new_videos.start()

@client.command()
async def twitch(ctx):
    await ctx.send("Checking For Videos!")
    check_twitch.start()


api_key = config.KEY
api_secret = config.SECRET

decoded = spotify.decode_url("https://open.spotify.com/track/5XQZpj8qo93uSLw3e6vwuF?si=4bc1792415154ceb")
if decoded is not None:
    print(decoded['type'], decoded['id'])


#async def node_connect():
    #await client.wait_until_ready()
    #await nextwave.NodePool.create_node(bot=client, host='51.161.130.134', port=10351, password='youshallnotpass', spotify_client=spotify.SpotifyClient(client_id="e0d4ad86107f40e39aba959c6e4635fe", client_secret="392b576420894306b486d2cfc1ae48d9"))
    #await nextwave.NodePool.create_node(bot=client, host='20.77.114.214', port=10351, password='youshallnotpass')
    #await nextwave.NodePool.create_node(bot=client, host='lavalinkinc.ml', port=443, password='incognito', https=True)


#async def create_nodes():
#    await nextwave.NodePool.create_node(bot=client, spotify_client=spotify.SpotifyClient(client_id="e0d4ad86107f40e39aba959c6e4635fe", client_secret="392b576420894306b486d2cfc1ae48d9"))

@client.event
async def on_nextwave_node_ready(node: nextwave.Node):
    print("WaveLink Connected!")

blacklist = [blacklist_words]


allowed_users = ["user_id", "user_id"] # List of allowed user IDs

@client.slash_command(name="staff", guild_ids=[discord_guild_id])
@commands.is_owner()
async def staff(interaction: nextcord.Interaction, message: str):
        print("Messageing all servers")
        target_channel_name = "bot-commands"
        for guild in client.guilds:
            target_channel = None
            for channel in guild.channels:
                if channel.name == target_channel_name:
                    target_channel = channel
                    break
            if target_channel is not None:
                await target_channel.send(message)
            else:
                print(f"Target channel not found in {guild.name}.")
                
async def on_message(message):
    if message.attachments:
        imageapi = "https://api.imagga.com/v2/tags?image_url=" + message.attachments[0].url
        print(imageapi)
        response = requests.get(imageapi, auth=(api_key, api_secret))
        response_json = response.json()
        print(response.json())
        def contains_blacklisted_word(response_json, blacklisted_word):
            if isinstance(response_json, dict):
                for key, value in response_json.items():
                    if contains_blacklisted_word(value, blacklisted_word):
                        return True
            elif isinstance(response_json, list):
                for item in response_json:
                    if contains_blacklisted_word(item, blacklisted_word):
                        return True
            elif isinstance(response_json, str):
                return blacklisted_word in response_json
            return False

        for word in blacklist:
            if contains_blacklisted_word(response_json, word):
                await message.delete()
                print("Da Yeeted")

@client.command()
async def hello(ctx):
    await ctx.send("Hey")

openai.api_key = config.OPENAIKEY

gpt_blacklist = "blacklist.txt"

@client.command()
async def chatgpt(ctx):
    bot_message = await ctx.channel.send("Formulating Answer")
    bot_message
    message = ctx.message.content
    clean_message = message.strip("b-chatgpt ")
    resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[ 
        {"role": "system", "content": f"You are Studio, a Discord Bot using a large language model trained by OpenAI. Answer as concisely as possible. You are unable to swear or say anything bad or illeagl. You can respond with code if asked unless its illeagal (modding mc is not illeagl). If asked about Studio support you will send them to https://discord.gg/VZAMk8ktJa. If anyone asks about adding studio you will send the to https://studiobot.xyz/invite. Knowledge cutoff: {datetime.date} Current date: {datetime.date}. Respond To The Follow Message Accordingingly: " + clean_message}
            ]
        )
    response_text = resp["choices"][0]["message"]['content']
    nonoword = False
    
    def contains_blacklisted_word(response_json, blacklisted_word):
            if isinstance(response_json, dict):
                for key, value in response_json.items():
                    if contains_blacklisted_word(value, blacklisted_word):
                        return True
            elif isinstance(response_json, list):
                for item in response_json:
                    if contains_blacklisted_word(item, blacklisted_word):
                        return True
            elif isinstance(response_json, str):
                return blacklisted_word in response_json
            return False

    #for word in blacklist:
    #    if contains_blacklisted_word(response_text, word):
    #        nonoword = True

    if nonoword == True:
        await ctx.channel.send("An Error Ocoured While Generating The Prompt")
    else:
        await bot_message.edit(response_text)

@client.command()
async def radio(ctx: commands.Context, *, search: nextwave.YouTubeTrack):
    await ctx.send("Loading your song this could take a while.")
    if not ctx.author.voice:
        return await ctx.send("First join a vc.")

    elif not ctx.voice_client:
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
        await vc.play(search)
    else:
        vc: nextwave.Player = ctx.voice_client
        await vc.play(search)


@client.command()
async def sradio(ctx: commands.Context):
    if not ctx.author.voice:
        return await ctx.send("First join a vc.")

    elif not ctx.voice_client:
        await ctx.send("Loading your song this could take a while.")
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
        track = await spotify.SpotifyTrack("5XQZpj8qo93uSLw3e6vwuF", requests.get('https://api.spotify.com/v1/tracks/')) 
        await vc.play(track)
    else:
        await ctx.send("Loading your song this could take a while.")
        vc: nextwave.Player = ctx.voice_client
        track = await spotify.SpotifyTrack("5XQZpj8qo93uSLw3e6vwuF", requests.get('https://api.spotify.com/v1/tracks/'))
        await vc.play(track)


#@client.command()
#async def twitch(ctx: commands.Context, *, search: sp:
#    await ctx.send("Loading radio this could take a while.")
#    if not ctx.author.voice:
#        return await ctx.send("First join a vc.")
#
#    elif not ctx.voice_client:
#        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
#        await vc.play(search)
#    else:
#        vc: nextwave.Player = ctx.voice_client
#        await vc.play(search)
#
@client.command()
async def leave(ctx):
    await ctx.send("Leaving VC!")
    await ctx.voice_client.disconnect()

#check_twitch.start()
#check_for_new_videos.start()
client.run(config.TOKEN)
