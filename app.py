#############################################################################
# This is a cut down and commented version of another file and will not run #
# Any Comments starting with ###### are comments by me                      #
# This file is the bits of code I worked on for Studios dashboard (app.py)  #
#############################################################################

from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import discord
from discord.ext import commands, tasks
import aiosqlite
import asyncio
import config
from googleapiclient.discovery import build
import requests
import json
import sqlite3
from requests.structures import CaseInsensitiveDict


###### Define aBot ######
class aBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix="s~", intents=discord.Intents.all(), *args, **kwargs)
    ###### When the bot is ready print that it is up and connect to the database ######
    async def on_ready(self):
        print(f"Bot is up and ready | Logged in as {self.user}")
        self.db = await aiosqlite.connect('Studio.db')
        await asyncio.sleep(3)
        ###### Create tables in the database if they dont already exsist ######
        async with client.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS discord_youtube (discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text, id integer, enabled text)")
            await client.db.commit()
            await cursor.execute("CREATE TABLE IF NOT EXISTS discord_twitch (discord_channel_id integer, twitch_channel_id text, is_live interger, failed_last_send text, enabled text, id integer)")
            await client.db.commit()
            print("Database Servers Started")
###### Define client this is how we connect to the discord bot ######
client = aBot()

app = Quart(__name__)

###### This is how we render pages spesifically this is how we render the socials page (social.html) ######
@app.route("/dashboard/<int:guild_id>/socials")
async def dashboardSocial(guild_id):
    ###### If the user accessing the dashboard is not autherised then it redirects to /login/ ######
    if not await discord.authorized:
        return redirect("/login/")
    ###### Sets the guild (Server) that we are currently accessing ######
    guild = client.get_guild(guild_id)
    ###### If the guild is None it redirects to an invite for the bot ######
    if guild is None:
        return redirect("https://studiobot.xyz/invite")
    ###### Else it pulls the data about the guild that we want ######
    else:
        guild_data = {
            "name": guild.name,
            "id": guild.id,
            "channels": guild.text_channels,
            "guildIcon": guild.icon
	    }
    ###### And then renders in using social.html ######    
    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])
###### This is a post to url for the youtube notifications code in social.html and adds the info needed for the youtube code (Line 150) ######
@app.route("/dashboard/<int:guild_id>/youtube", methods=["POST"])
async def dashboardSocialPOST(guild_id):
    if not await discord.authorized:
        return redirect("/login/")
    
    guild = client.get_guild(guild_id)

    if guild is None:
        return redirect("https://studiobot.xyz/invite")
    else:
        guild_data = {
            "name": guild.name,
            "id": guild.id,
            "channels": guild.text_channels,
            "guildIcon": guild.icon
	    }
    ###### Sets YoutubeEnabled to the request.json() and YoutubeEnabled1 to the isYoutubeEnabled element of YoutubeEnabled ######      
    YoutubeEnabled = await request.get_json()
    YoutubeEnabled1 = YoutubeEnabled["isYoutubeEnabled"]
    ###### Sets YoutubeChannel to the request.json() and YoutubeChannel1 to the setYoutube element of YoutubeChannel ######
    YoutubeChannel = await request.get_json()
    YoutubeChannel1 = YoutubeChannel["setYoutube"]
    ###### Sets DiscordChannel to the request.json() and DiscordChannel1 to the setChannel element of DiscordChannel ######
    DiscordChannel = await request.get_json()
    DiscordChannel1 = DiscordChannel["setChannel"]
    ###### Connect to the database ######
    async with aiosqlite.connect('Studio.db') as db:
        async with db.cursor() as cursor:
            ###### Check if there is already a youtube channel set for the guild id if there is it updates it if not then it adds it ######
            await cursor.execute("SELECT youtube_channel_id, discord_channel_id, enabled FROM discord_youtube WHERE id = ?", (guild_id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute(f"UPDATE discord_youtube SET youtube_channel_id = ?, discord_channel_id = ?, enabled =? WHERE id = ?", (YoutubeChannel1, DiscordChannel1, YoutubeEnabled1, guild_id,))
            else:
                await cursor.execute("INSERT INTO discord_youtube (youtube_channel_id, discord_channel_id, enabled, id) VALUES (?, ?, ?, ?)", (YoutubeChannel1, DiscordChannel1, YoutubeEnabled1, guild_id,))
        await db.commit()
    ###### And then renders the socials page ######
    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])
###### This is a post to url for the twitch notifications code in social.html and adds the data needed for the twitch code (Line 218) ######
@app.route("/dashboard/<int:guild_id>/twitch", methods=["POST"])
async def dashboardTwitchPOST(guild_id):
    if not await discord.authorized:
        return redirect("/login/")
    
    guild = client.get_guild(guild_id)

    if guild is None:
        return redirect("https://studiobot.xyz/invite")
    else:
        guild_data = {
            "name": guild.name,
            "id": guild.id,
            "channels": guild.text_channels,
            "guildIcon": guild.icon
	    }
    ###### Sets TwitchEnabled to the request.json() and TwitchEnabled1 to the isTwitchEnabled element of TwitchEnabled ######       
    TwitchEnabled = await request.get_json()
    TwitchEnabled1 = TwitchEnabled["isTwitchEnabled"]
    ###### Sets TwitchChannel to the request.json() and TwitchChannel1 to the setTwitch element of TwitchChannel ######
    TwitchChannel = await request.get_json()
    TwitchChannel1 = TwitchChannel["setTwitch"]
    ###### Sets DiscordChannel to the request.json() and DiscordChannel1 to the setChannel element of DiscordChannel ######
    DiscordChannel = await request.get_json()
    DiscordChannel1 = DiscordChannel["setChannel"]
    ###### Connect to the database ######
    async with aiosqlite.connect('Studio.db') as db:
        async with db.cursor() as cursor:
            ###### Check if there is already a twitch channel set for the guild id if there is it updates it if not then it adds it ######
            await cursor.execute("SELECT twitch_channel_id, discord_channel_id, enabled FROM discord_twitch WHERE id = ?", (guild_id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute(f"UPDATE discord_twitch SET twitch_channel_id = ?, discord_channel_id = ?, enabled =? WHERE id = ?", (TwitchChannel1, DiscordChannel1, TwitchEnabled1, guild_id,))
            else:
                await cursor.execute("INSERT INTO discord_twitch (twitch_channel_id, discord_channel_id, enabled, id) VALUES (?, ?, ?, ?)", (TwitchChannel1, DiscordChannel1, TwitchEnabled1, guild_id,))
        await db.commit()
    ###### And then renders the socials page ######
    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

###### Sets up the youtube API stuff we need ###### 
youtube = build('youtube', 'v3', developerKey=config.YOUTUBEKEY)
###### Connects to the database ###### 
conn = sqlite3.connect('studio.db')
c = conn.cursor()

###### This is a task that loos every 1 minutes pretty self explanitry ###### 
@tasks.loop(minutes=1)
async def check_youtube():
    ###### Sleep for 60 seconts to allow the database to inisilize ###### 
    await asyncio.sleep(60)
    print("Running YT")
    ###### Select all of the channels from the database ###### 
    c.execute('SELECT youtube_channel_id FROM discord_youtube')
    channel_ids = c.fetchall()
    ###### For all of the channel ids in channel_ids it searches for the channel id ###### 
    for channel_id in channel_ids:
        search_response = youtube.search().list(
            channelId=channel_id,
            type='video',
            part='id,snippet',
            order='date',
            maxResults=1
        ).execute()
        
        ###### If there is data in items get the channel name and latest video ID from the response ###### 
        if search_response['items']:
            latest_video_id = search_response['items'][0]['id']['videoId']
            channel_name = search_response['items'][0]['snippet']['channelTitle']
        ###### Else continue ###### 
        else:
            continue
        
        ###### Pull the data we need from the database ######
        c.execute('SELECT latest_video_id, discord_channel_id, failed_last_send, enabled FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
        row = c.fetchone()
        ###### if the data we need is there then we set the variables we need ######
        if row is not None:
            previous_video_id, discord_channel_id, failed_last_send, ytenabled = row
            ###### Check if latest video ID is not the same as the previous video ID ###### 
            if latest_video_id != previous_video_id:
                ###### Update the database ######
                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, channel_id))
                conn.commit()
                ###### If ther is a discord channel id and ytenabled is equal to 'on' then send the notification ######
                if discord_channel_id != 0 and discord_channel_id is not None and ytenabled == 'on':
                    # Post video in Discord channel
                    channel = client.get_channel(discord_channel_id)
                    await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', channel_id))
                    conn.commit()
                ###### Else set failed_last_send to true ######
                else:
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', channel_id))
                    conn.commit()
            ###### If the video ids are the same then it checks if failed_last_send is true and if it is tries to send it again ######
            else:
                if failed_last_send == 'True':
                    channel1 = client.get_channel(discord_channel_id)
                    if discord_channel_id != 0 and discord_channel_id is not None and ytenabled == 'on':
                        ###### If there is a discord channel and ytenabled is equal to 'on' then send away ######
                        await channel1.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', channel_id))
                        conn.commit()
                    ###### Else continue ######
                    else:
                        continue
                ###### Else continue ######
                else:
                    continue
        ###### Else continue ######
        else:
            continue

###### Loop to check twitch channels ######
@tasks.loop(minutes=1)
async def check_twitch():
    ###### sleep for 60 seconds to let the database start ######
    await asyncio.sleep(60)
    print("Running Twitch")
    ###### setting the variables we may or may noy need ######
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET

    ###### Get a list of channels from the database ######
    ccursor = conn.execute("SELECT twitch_channel_id, is_live FROM discord_twitch")
    channel_info = ccursor.fetchall()

    ###### Get an access token with the client ID and secret ######
    url = 'https://id.twitch.tv/oauth2/token'
    headd = CaseInsensitiveDict()
    headd["Content-Type"] = "application/x-www-form-urlencoded"
    dat = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope=channel%3Aread%3Asubscriptions"
    response = requests.post(url, headers=headd, data=dat)
    ###### if the response code is not 200 then print an error message ######
    if response.status_code != 200:
        print(f"Error getting access token: {response.text}")
        return
    ###### setting the variables we need to check if a channel is live ######
    data = json.loads(response.text)
    access_token = data['access_token']
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}',
    }
    ###### for each channel in the data base ping the twitch api asking for info on them ######
    for channel in channel_info:
        channel_name = channel[0]
        is_live = channel[1]
        req_url = f'https://api.twitch.tv/helix/search/channels?query={channel_name}'
        req_response = requests.get(req_url, headers=headers)
        ###### if the response code is not 200 then print an error message ######
        if req_response.status_code != 200:
            print(f"Error getting channel info for {channel_name}: {response.text}")
            continue
        req_data = json.loads(req_response.text)
        ###### if req_data has data then attempt to pull data from the 10th row in the array ######
        if req_data['data']:
            try:
                channel_isLive1 = req_data['data'][9]['is_live']
                channel_isLive1
                ###### If we succeed in pulling the data then get the info we need from it ######
                if channel_isLive1 == True:
                    game_name_fake = req_data['data'][9]['game_name']
                    user_name_fake = req_data['data'][9]['display_name']
                    title_fake_fake = req_data['data'][9]['title']
                    ###### check if is_live is true if it is update the data base and pull the discord channel id ######
                    if not is_live:
                            # Update is_live column to True
                            conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                            conn.commit()
                            cccursor = conn.execute(f"SELECT discord_channel_id, enabled FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                            discord_info, enabled = cccursor.fetchone()
                            ###### check if the discord channel id is not 0 and enabled is set to on ######
                            if discord_info != 0 and discord_info != None and enabled == 'on':
                                    ###### Send the notification ######
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_fake} Is Live Playing {game_name_fake}! {title_fake_fake} https://twitch.tv/{channel_name}")
                            ###### Else continue ######
                            else:
                                    continue
                    ###### Else continue ######
                    else:
                            continue
                ###### Else continue ######
                else:
                    continue
            ###### if we get an error (which we are expecting) attempt to pull data from the 2nd row of the array ######
            except IndexError:
                try:
                    channel_isLive = req_data['data'][1]['is_live']
                    channel_isLive
                    ###### if we succeed then we check if the is_live element is true if it is then we pull the data we need ######
                    if channel_isLive == True:
                        game_name = req_data['data'][1]['game_name']
                        user_name = req_data['data'][1]['display_name']
                        title_fake = req_data['data'][1]['title']
                        ###### if the channel is not marked as live already then update the database ######
                        if not is_live:
                                if not is_live: ###### idk why there is 2 ######
                                    conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                    conn.commit()
                                    ###### pull the discord channel id
                                    cccursor = conn.execute(f"SELECT discord_channel_id, enabled FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                    discord_info, enabled = cccursor.fetchone()
                                    ###### if its not 0 or none and enabled is set to on then send the notification ######
                                    if discord_info != 0 and discord_info != None and enabled == 'on':
                                        channel = client.get_channel(discord_info)
                                        await channel.send(f"{user_name} Is Live Playing {game_name}! {title_fake} https://twitch.tv/{channel_name}")
                                    else:
                                        continue
                        else:
                                continue
                    else:
                        continue
                ###### after another error we get to the last of these ######
                except IndexError:
                    ###### appart from thos one ######
                    try:
                            ###### check if we can pull data from the 2nd row again ######
                            title = req_data['data'][1]['title']
                            title
                            ###### if we can then update the database ######
                            conn.execute(f"UPDATE discord_twitch SET is_live = 0 WHERE twitch_channel_id = '{channel_name}'")
                            conn.commit()
                    ###### after another error we pull the data from the 1st row of the array ######
                    except IndexError:
                            game_name_real = req_data['data'][0]['game_name']
                            user_name_real = req_data['data'][0]['display_name']
                            title_real = req_data['data'][0]['title']
                            ###### if the channel is not marked as live we change that ######
                            if not is_live:
                                conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                conn.commit()
                                ###### pull the discord channel id ######
                                cccursor = conn.execute(f"SELECT discord_channel_id, enabled FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                discord_info, enabled = cccursor.fetchone()
                                ###### if its not 0 or None and enabled is equal to on SEND! ######
                                if discord_info != 0 and discord_info != None and enabled == 'on':
                                    # Post video in Discord channel
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_real} Is Live Playing {game_name_real}! {title_real} https://twitch.tv/{channel_name}")
                                else:
                                    continue
                            else:
                                continue

if __name__ == "__main__":
    ###### this gets and event loop ######
    loop = asyncio.get_event_loop()
    ###### sets the tasks ######
    tasks = [check_youtube.start(), check_twitch.start()]
    ###### and runs them till there complete ######
    loop.run_until_complete(asyncio.gather(*tasks))
