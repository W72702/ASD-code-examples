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

######## Setting up the intents for discord ########
intents = nextcord.Intents.default()
intents.message_content = True

######## Setting up the bot and setting a preffix ########
client = commands.Bot(command_prefix="b-", intents=intents)

######## When the bot is ready it prints to the terminal ########
@client.event
async def on_ready():
    print("Bot Is Online")

######## An old function to add youtube channels to the database an be uncommented and used if needed ########
#async def add_channels():
#    for channel_id in channel_ids:
#        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel, 'youtube_id'))
#        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel, 'youtube_id'))
#        c.execute('SELECT youtube_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
#        existing_channel = c.fetchone()
#        if existing_channel:
#            print(f"{channel_id} already added, skipping")
#            continue
#        else:
#            c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (channel_id,))
#            conn.commit()
#            print(f"Added {channel_id}")

######## Old version of the on_ready thats above ########    
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

######## Setting up the youtube data API client config.YOUTUBEKEY is the dev key that is declared in config.py (Not uploaded) ########
youtube = build('youtube', 'v3', developerKey=config.YOUTUBEKEY)
######## Declaring the discord channel that notifications were sent to ########
#DISCORD_CHANNEL_ID = discord_channel

######## Old command that update the discord channel that the youtube and twitch notifications where sent to ########
#@client.command()
#async def channel(ctx):
#    set(CHANNEL_ID = {ctx.message.content}) 

######## Lists that where used in older versions of this bot ########
#channel_ids = []

#discord_ids = []

######## twitch channels that it used to check to see if they where live but is not needed in the current version ########
#twitch_channelss = ['twitch1', 'twitch2']

######## Start a discord task that loops every minute ########
@tasks.loop(minutes=1)
async def check_twitch():
    ######## More config.py variables ########
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET
    
    ######## Connect to database ########
    con1 = sqlite3.connect('discord_twitch.db')
    c1 = con1.cursor()
    ######## Create a table in the database if one does not already exsist ########
    c1.execute('''CREATE TABLE IF NOT EXISTS discord_twitch
                (server_name, discord_channel_id integer, twitch_channel_id text, is_live interger, failed_last_send text)''')
    con1.commit()
    ######## Get list of channels from database ########
    ccursor = con1.execute("SELECT twitch_channel_id, is_live FROM discord_twitch")
    channel_info = ccursor.fetchall()
    
    ######## Open a text file and read the contents then set it as a list ########
    with open('twitch_channels.txt', 'r') as f:
        channels_from_file = set(f.read().split())

    ######## Add any missing channels to the database ########
    for channel_name in channels_from_file:
        if not any(channel_name == row[0] for row in channel_info):
            print(f"Adding Channel {channel_name}")
            c1.execute("INSERT INTO discord_twitch VALUES (?, ?, ?, ?, ?)", ("", 0, channel_name, 0, ""))
            con1.commit()
            
    ######## Get an access token from twitch with client ID and secret ########
    url = 'https://id.twitch.tv/oauth2/token'
    headd = CaseInsensitiveDict()
    headd["Content-Type"] = "application/x-www-form-urlencoded"
    dat = f"client_id={config.CLIENT_ID}&client_secret={config.CLIENT_SECRET}&grant_type=client_credentials&scope=channel%3Aread%3Asubscriptions"
    response = requests.post(url, headers=headd, data=dat)
    
    ######## If the response code is not 200 then print a message to the terminal and then return ########
    if response.status_code != 200:
        print(f"Error getting access token: {response.text}")
        return
    data = json.loads(response.text)
    
    ######## Grab the access token from the response ########
    access_token = data['access_token']
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
    }
    
    ######## For each channel in the database ping the twitch API so see if there live ########
    for channel in channel_info:
        channel_name = channel[0]
        is_live = channel[1]
        req_url = f'https://api.twitch.tv/helix/search/channels?query={channel_name}'
        req_response = requests.get(req_url, headers=headers)
        if req_response.status_code != 200:
            print(f"Error getting channel info for {channel_name}: {response.text}")
            continue
        req_data = json.loads(req_response.text)
        ######## Pause ########
        time.sleep(2)
        ######## If there is data in the response then continue ########
        if req_data['data']:
            ######## Check if there is a is_live variable in the 10th row of the array if there is continue if there isn't fail ########
            try:
                channel_isLive1 = req_data['data'][9]['is_live']
                channel_isLive1
                ######## Checks if the is_live element is set to true if is is then pull the data we want ########
                if channel_isLive1 == True:
                    game_name_fake = req_data['data'][9]['game_name']
                    user_name_fake = req_data['data'][9]['display_name']
                    title_fake_fake = req_data['data'][9]['title']
                    ######## Check if the is_live variable is set if not then update it to true ########
                    if not is_live:
                            con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                            con1.commit()
                            ######## Pull the discord channel id from the database ########
                            cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                            discord_info = cccursor.fetchone()
                            ######## If it is equal to 0 sleep if not post a notification ########
                            if discord_info != 0:
                                    ######## SEND! ########
                                    channel = client.get_channel(discord_info)
                                    ######## Extra Info: these are all have fake after to seperate them from the upcoming variables that where all called the same thing ########
                                    await channel.send(f"{user_name_fake} Is Live Playing {game_name_fake}! {title_fake_fake} https://twitch.tv/{channel_name}")
                            else:
                                ######## Snooze for 2 seconds ########
                                time.sleep(2)
                    else:
                        ######## If is_live is true then continue ########
                        continue
                ######## If the is_live element is set to false then continue ########
                else:
                    continue
            ######## If the above checks throw an IndexError (Which in this case is expected) then check if the is_live element is set in the 2nd row of the array if there isn't fail ########
            except IndexError:
                try:
                    channel_isLive = req_data['data'][1]['is_live']
                    channel_isLive
                    ######## If channel_isLive is equal to true then pull the data we need ########
                    if channel_isLive == True:
                        game_name = req_data['data'][1]['game_name']
                        user_name = req_data['data'][1]['display_name']
                        title_fake = req_data['data'][1]['title']
                        ######## Idk why there is two of these but there is ########
                        if not is_live:
                                ######## if the is_live variable is not true then set it to true ########
                                if not is_live:
                                    # Update is_live column to True
                                    con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                    con1.commit()
                                    ######## Pull the discord channel ########
                                    cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                    discord_info = cccursor.fetchone()
                                    ######## If it is not equal to 0 then send the notification to the channel ########
                                    if discord_info != 0:
                                        channel = client.get_channel(discord_info)
                                        await channel.send(f"{user_name} Is Live Playing {game_name}! {title_fake} https://twitch.tv/{channel_name}")
                                    ######## Else snooze ########
                                    else:
                                        time.sleep(2)
                        ######## Else continue ########
                        else: 
                           continue
                    ######## Else continue (there is alot of these)
                    else:
                        continue
                ######## If it errors then pull the title from the second row of the array and attempt to set the is_live variable to false ########
                except IndexError:
                    try:
                            title = req_data['data'][1]['title']
                            title
                            con1.execute(f"UPDATE discord_twitch SET is_live = 0 WHERE twitch_channel_id = '{channel_name}'")
                            con1.commit()
                    ######## If that fails then pull the data we need from the first row of the array ########
                    except IndexError:
                            game_name_real = req_data['data'][0]['game_name']
                            user_name_real = req_data['data'][0]['display_name']
                            title_real = req_data['data'][0]['title']
                            ######## If the is_live variable is set to false set it to true ########
                            if not is_live:
                                # Update is_live column to True
                                con1.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                con1.commit()
                                ######## Pull the discord channel id ########
                                cccursor = con1.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                discord_info = cccursor.fetchone()
                                ######## If it doesnt equal 0 send the notification ########
                                if discord_info != 0:
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_real} Is Live Playing {game_name_real}! {title_real} https://twitch.tv/{channel_name}")
                                else:
                                    ######## Else snooze (ik im reapeating my self alot atm)
                                    time.sleep(2)
                            ######## Else continue ########
                            else:
                                continue


######## Connect to another database ########
conn = sqlite3.connect('discord_youtube.db')
c = conn.cursor()
######## Create the table if it doesnt exsist ########
c.execute('''CREATE TABLE IF NOT EXISTS discord_youtube
                (server_name, discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text)''')
conn.commit()

######## Old task used to update the databases from files this was moved to the functions themselves ########
#@tasks.loop(minutes=1)
#async def update_db():
#    with open('youtube.txt', 'r') as f:
#        ids = f.readlines()
#        for channel_id in ids:
#            c.execute('SELECT youtube_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
#            existing_channel = c.fetchone()
#            if existing_channel:
#                print(f"{channel_id} already added, skipping")
#                continue
#            else:
#                c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (channel_id,))
#                conn.commit()
#                print(f"Added {channel_id}")
#                continue
#@tasks.loop(minutes=1)
#async def update_db1():
#    with open('discord.txt', 'r') as f:
#        ids2 = f.readlines()
#        for discord_id in ids2:
#            c.execute('SELECT discord_channel_id FROM discord_youtube WHERE discord_channel_id = ?', (discord_id,))
#            existing_channel = c.fetchone()
#            if existing_channel:
#                print(f"{discord_id} already added, skipping")
#                continue
#            else:
#                c.execute('INSERT INTO discord_youtube (discord_channel_id) VALUES (?)', (discord_id,))
#                conn.commit()
#                print(f"Added {discord_id}")
#                continue


######## Old Check for new videos task ########
#@tasks.loop(minutes=1)
#async def check_for_new_videosa():
#    for channel_id in channel_ids:
#        print(f"Searching For Videos On {channel_id}")
#        search_response = youtube.search().list(
#            channelId=channel_id,
#            type='video',
#            part='id, snippet',
#            order='date',
#            maxResults=1
#        ).execute()
#        c.execute('SELECT latest_video_id FROM discord_youtube')
#        previous_video_ids = [row[0] for row in c.fetchall()]
#        if search_response['items']:
#            latest_video_id = search_response['items'][0]['id']['videoId']
#            channel_name = search_response['items'][0]['snippet']['channelTitle']
#            if latest_video_id in previous_video_ids:
#                print("No New Videos")
#            else:
#                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, channel_id))
#                conn.commit()
#                channel = client.get_channel(DISCORD_CHANNEL_ID)
#                await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
#        else:
#            print("No new videos found.")

######## The current task for check for videos ########
@tasks.loop(minutes=1)
######## declate the function name ########
async def check_for_new_videos():
    ######## Open a text file and set the contents as a list ########
    with open('youtube.txt', 'r') as f:
        yt_ids = f.readlines()
        ######## For each youtube channel in that list check if it in the database if it is then skip it if its not then add it ########
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
            ######## Open another file and set its contents to a list ########
            with open('discord.txt', 'r') as f:
                discord_ids = f.readlines()
                ######## for each discord channel id in that list then checck if its in the data base if it is then skip it if its not then add it ########
                for discord_channel_id in discord_ids:
                    discord_channel_id = discord_channel_id.strip()
                    if existing_discord_channel_id == discord_channel_id:
                        print(f"Discord ID already set for {yt_channel_id}, skipping")
                        continue
                    else:
                        c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE row = ?', (discord_channel_id, row_id,))
                        conn.commit()
                        print(f"Added {discord_channel_id} for {yt_channel_id}")
######## Pull all youtube channel ids from the database and add them to a list ########
    cursorr = conn.execute("SELECT youtube_channel_id FROM discord_youtube")
    channel_ids = cursorr.fetchall()
    ######## For every id in that list send a request to the youtube api ########
    for yt_channel_id in channel_ids:
        print(f"Searching For Videos On {yt_channel_id}") ######## Debug Print ########
        search_response = youtube.search().list(
            channelId=yt_channel_id,
            type='video',
            part='id,snippet',
            order='date',
            maxResults=1
        ).execute()
        
        ######## If there is data in 'itemsl then get the channel name and latest video ID from the response ########
        if search_response['items']:
            latest_video_id = search_response['items'][0]['id']['videoId']
            channel_name = search_response['items'][0]['snippet']['channelTitle']
        ######## Else print and continue ########
        else:
            print("No new videos found.")
            continue
        
        ######## Grab everything we need from the database ########
        c.execute('SELECT latest_video_id, discord_channel_id, failed_last_send FROM discord_youtube WHERE youtube_channel_id = ?', (yt_channel_id,))
        row = c.fetchone()
        ######## if the data is not none set the previous video id discord channel id and faild last send variables to the data ########
        if row is not None:
            previous_video_id, discord_channel_id, failed_last_send = row
            ######## Check if latest video ID is different from the last video if of the channel ########
            if latest_video_id != previous_video_id:
                ######## If it is update the video id to the latest ########
                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, yt_channel_id))
                conn.commit()
                ######## If the discord channel id variable is not empty then set the channel to send the notification to the discord channel id ########
                if discord_channel_id:
                    channel = client.get_channel(discord_channel_id)
                    ######## If the discord channel id is not 0 the nsend the notification ########
                    if discord_channel_id != 0:
                        await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', yt_channel_id))
                        conn.commit()
                        print(f"New video posted in Discord channel {discord_channel_id}") ######## Another debug print ########
                    ######## If it is 0 then print to the console and set failed last send to true ########
                    else:
                        print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', yt_channel_id))
                        conn.commit()
                ######## If there is no discord channel id print and set faild last send to true ########
                else:
                    print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', yt_channel_id))
                    conn.commit()
            ######## If the video id is the same as the previous video id then check if the failed last send variable is set to true ########
            else:
                if failed_last_send == 'True':
                    ######## If it is then set the channel to send the notification to its not a 0 or None then send the notification ########
                    channel1 = client.get_channel(discord_channel_id)
                    if discord_channel_id is not None and not 0:
                        await channel1.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        ######## Set failed last send to false ########
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', yt_channel_id))
                        conn.commit()
                    ######## If the discord channel id is 0 or None then continue ########
                    else:
                        print(f"No Discord channel ID set for YouTube channel {yt_channel_id}")
                ######## If the failed last send variable is flase then continue ########
                else:
                    print("No new videos")
        ######## If the data we got at the begining was empty continue ########
        else:
            print(f"No entry found in database for YouTube channel {yt_channel_id}")



######## Manually checks for videos ########
@client.command()
async def videos(ctx):
    await ctx.send("Checking For Videos!")
    check_for_new_videos.start()

######## Manially check if people are live ########
@client.command()
async def twitch(ctx):
    await ctx.send("Checking For Videos!")
    check_twitch.start()

######## More config.py ariables this time for image recognition ########
api_key = config.KEY
api_secret = config.SECRET

######## Decode a spotify URL and print the decode values to the console ########
decoded = spotify.decode_url("https://open.spotify.com/track/5XQZpj8qo93uSLw3e6vwuF?si=4bc1792415154ceb")
if decoded is not None:
    print(decoded['type'], decoded['id'])

######## Connect to a lavalink server ########
#async def node_connect():
    #await client.wait_until_ready()
    ######## there is alot if server here ########
    #await nextwave.NodePool.create_node(bot=client, host='51.161.130.134', port=10351, password='youshallnotpass', spotify_client=spotify.SpotifyClient(client_id="e0d4ad86107f40e39aba959c6e4635fe", client_secret="392b576420894306b486d2cfc1ae48d9"))
    #await nextwave.NodePool.create_node(bot=client, host='20.77.114.214', port=10351, password='youshallnotpass')
    #await nextwave.NodePool.create_node(bot=client, host='lavalinkinc.ml', port=443, password='incognito', https=True)

######## create a wavelink node ########
#async def create_nodes():
#    await nextwave.NodePool.create_node(bot=client, spotify_client=spotify.SpotifyClient(client_id="e0d4ad86107f40e39aba959c6e4635fe", client_secret="392b576420894306b486d2cfc1ae48d9"))

######## on the succesful connection of the node print to console ########
@client.event
async def on_nextwave_node_ready(node: nextwave.Node):
    print("WaveLink Connected!")

######## This would be a list of blacklisted words for the image recognition stuff thats coming up ########
blacklist = [blacklist_words]

######## a list of allowed discord user ids for the staff command bellow ########
allowed_users = ["user_id", "user_id"] # List of allowed user IDs

######## Staff command ########
@client.slash_command(name="staff", guild_ids=[discord_guild_id])
@commands.is_owner()
async def staff(interaction: nextcord.Interaction, message: str):
    ######## This sends a message to all servers that the bot is in ########
        print("Messageing all servers")
        ######## Set a target channel ########
        target_channel_name = "bot-commands"
        ######## For each server the bot is in set the target channel to None and then check if the server has a channel called bot commands if it does then set the target channel to bot commands ########
        for guild in client.guilds:
            target_channel = None
            for channel in guild.channels:
                if channel.name == target_channel_name:
                    target_channel = channel
                    break
            ######## If the target channel is not none send a message to the target channel ########
            if target_channel is not None:
                await target_channel.send(message)
            ######## Else skip the server ######## 
            else:
                print(f"Target channel not found in {guild.name}.")
######## That image recogntion thing I was talking about earlier ########
######## When a message is sent if that message is an attachment then send it to the image recognition api ########
async def on_message(message):
    if message.attachments:
        imageapi = "https://api.imagga.com/v2/tags?image_url=" + message.attachments[0].url
        ######## Print the url (this was for debugging) ########
        print(imageapi)
        response = requests.get(imageapi, auth=(api_key, api_secret))
        response_json = response.json()
        ######## Make a request then print it to the console ########
        print(response.json())
        ######## Check if the reponse from the image reognition api has any of the blacklisted words in it ########
        def contains_blacklisted_word(response_json, blacklisted_word):
            if isinstance(response_json, dict):
                for key, value in response_json.items():
                    if contains_blacklisted_word(value, blacklisted_word):
                        ######## If it does then it returns true ########
                        return True
            elif isinstance(response_json, list):
                for item in response_json:
                    if contains_blacklisted_word(item, blacklisted_word):
                        ######## If it does then it returns true ########
                        return True
            elif isinstance(response_json, str):
                return blacklisted_word in response_json
            ######## Else it returns false ########
            return False
        ######## For each word in the response it checks if its in the blacklist ########
        for word in blacklist:
            if contains_blacklisted_word(response_json, word):
                ######## If it does it deletes it ########
                await message.delete()
                print("Da Yeeted")
######## Command to say hello ########
@client.command()
async def hello(ctx):
    await ctx.send("Hey")

######## Set up for the OpenAI stuff bellow ########
openai.api_key = config.OPENAIKEY

######## Another blacklist this time telling the bot what to not allow ChatGPT to say ########
gpt_blacklist = "blacklist.txt"

######## When someone runs the command then send a response ########
@client.command()
async def chatgpt(ctx):
    bot_message = await ctx.channel.send("Formulating Answer")
    bot_message
    ######## Get the message contnet from the command this still includes the prefix ########
    message = ctx.message.content
    ######## Remove the prefix ########
    clean_message = message.strip("b-chatgpt ")
    ######## Set up the request to the OpenAI api ########
    resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
        ######## Telling the AI what it can and cant do and then asking it to respond to the message sent be the user ########
            messages=[ 
        {"role": "system", "content": f"You are Studio, a Discord Bot using a large language model trained by OpenAI. Answer as concisely as possible. You are unable to swear or say anything bad or illeagl. You can respond with code if asked unless its illeagal (modding mc is not illeagl). If asked about Studio support you will send them to https://discord.gg/VZAMk8ktJa. If anyone asks about adding studio you will send the to https://studiobot.xyz/invite. Knowledge cutoff: {datetime.date} Current date: {datetime.date}. Respond To The Follow Message Accordingingly: " + clean_message}
            ]
        )
    ######## Take the reponse and get the response from ChatGPT ########
    response_text = resp["choices"][0]["message"]['content']
    ######## Set nonoword to false ########
    nonoword = False
    ######## Blacklist word check ########
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
    ######## Commented out because we aren't useing it but this is what would check if there was a no no word in the response ########
    #for word in blacklist:
    #    if contains_blacklisted_word(re ponse_text, word):
    #        nonoword = True
    
    ######## If ther was a no no word then send an error ########
    if nonoword == True:
        await ctx.channel.send("An Error Ocoured While Generating The Prompt")
    ######## Else edit the original message sent at the begging to have the response from ChatGPT ########
    else:
        await bot_message.edit(response_text)
######## Youtube radio command (Does break Discord ToS so we are not implementing this to the full bot) ########
@client.command()
async def radio(ctx: commands.Context, *, search: nextwave.YouTubeTrack):
    ######## Send a message when the command is run ########
    await ctx.send("Loading your song this could take a while.")
    ######## If the user who ran the command is not a in a vc then send an error ########
    if not ctx.author.voice:
        return await ctx.send("First join a vc.")
    ######## Else join the vc and start playing the video (audio only) ########
    elif not ctx.voice_client:
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
        await vc.play(search)
    ######## If its already in the vc then it starts playing the video (audio only) ########
    else:
        vc: nextwave.Player = ctx.voice_client
        await vc.play(search)

######## Spotify radio (Currently not working) ########
@client.command()
async def sradio(ctx: commands.Context):
    ######## If the user is not in a vc send an error ########
    if not ctx.author.voice:
        return await ctx.send("First join a vc.")
    ######## If they are in a vc then send a message and join the vc and start playing the song (this is the bit thats not working) ########
    elif not ctx.voice_client:
        await ctx.send("Loading your song this could take a while.")
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
        track = await spotify.SpotifyTrack("5XQZpj8qo93uSLw3e6vwuF", requests.get('https://api.spotify.com/v1/tracks/')) 
        await vc.play(track)
    ######## If the bot is in the vc already start playing the song (this is also not working) ########
    else:
        await ctx.send("Loading your song this could take a while.")
        vc: nextwave.Player = ctx.voice_client
        track = await spotify.SpotifyTrack("5XQZpj8qo93uSLw3e6vwuF", requests.get('https://api.spotify.com/v1/tracks/'))
        await vc.play(track)

######## An old command that would play a twitch stream audio only in a vc ########
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

######## Command to leave the vc ########
@client.command()
async def leave(ctx):
    await ctx.send("Leaving VC!")
    await ctx.voice_client.disconnect()

######## Things to run the twitch and youtube notifications ########
#check_twitch.start()
#check_for_new_videos.start()
######## Login to the bot to make this all work ########
client.run(config.TOKEN)
