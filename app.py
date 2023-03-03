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



class aBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix="s~", intents=discord.Intents.all(), *args, **kwargs)

    async def on_ready(self):
        print(f"Bot is up and ready | Logged in as {self.user}")
        self.db = await aiosqlite.connect('Studio.db')
        await asyncio.sleep(3)
        async with client.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS guild_settings (guild_id INTEGER PRIMARY KEY, welcome_enabled INTEGER DEFAULT 0, welcome_message STRING, welcome_channel_id INTEGER)")
            await client.db.commit()
            await cursor.execute("CREATE TABLE IF NOT EXISTS discord_youtube (discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text, id integer, enabled text)")
            await client.db.commit()
            await cursor.execute("CREATE TABLE IF NOT EXISTS discord_twitch (discord_channel_id integer, twitch_channel_id text, is_live interger, failed_last_send text, enabled text, id integer)")
            await client.db.commit()
            print("Database Servers Started")
client = aBot()

app = Quart(__name__)
app.secret_key = b"random bytes representing quart secret key"
app.config["DISCORD_CLIENT_ID"] = 889429542584856607    # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "kbiCOohquAVZH7lrMg2aCaM6iy7C3J-j"                # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://localhost:3000/callback/"                 # URL to your callback endpoint.
app.config["DISCORD_BOT_TOKEN"] = "ODg5NDI5NTQyNTg0ODU2NjA3.GhQx4t.5JTsazooiGrsDdoeXw7zVwdUNkOgSzAteuQcXI"                    # Required to access BOT resources.

discord = DiscordOAuth2Session(app)

@app.route("/")
async def home():
    return await render_template("index.html", authorized = await discord.authorized)

@app.route("/login/")
async def login():
    return await discord.create_session()

@app.route("/callback/")
async def callback():
	try:
		await discord.callback()
	except Exception:
		pass
	return redirect(url_for("dashboard"))

@app.route("/dashboard/")
async def dashboard():
    if not await discord.authorized:
        return redirect("/login/")
    userGuilds = await discord.fetch_guilds()
    user = await discord.fetch_user()
    guild_count = len(client.guilds)
    guildIds = []
    for guild in client.guilds:
        guildIds.append(guild.id)
    
    guilds = []
    for guild in userGuilds:
        if guild.permissions.administrator:			
            guild.class_color = "green-border" if guild.id in guildIds else "red-border"
            guilds.append(guild)
            
    guilds.sort(key = lambda x: x.class_color == "red-border")
    
    return await render_template("dashboard.html",guild=guild, user=user, guildCount=guild_count, guilds=guilds)

@app.route("/dashboard/<int:guild_id>/info")
async def dashboardInfo(guild_id):
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

    return await render_template("info.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

@app.route("/dashboard/<int:guild_id>/welcoming")
async def dashboardWelcoming(guild_id):
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
        
    return await render_template("welcoming.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

@app.route("/dashboard/<int:guild_id>/socials")
async def dashboardSocial(guild_id):
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
        
    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

@app.route("/dashboard/<int:guild_id>/logging")
async def dashboardLogging(guild_id):
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
        
    return await render_template("logging.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

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
          
    YoutubeEnabled = await request.get_json()
    YoutubeEnabled1 = YoutubeEnabled["isYoutubeEnabled"]

    YoutubeChannel = await request.get_json()
    YoutubeChannel1 = YoutubeChannel["setYoutube"]

    DiscordChannel = await request.get_json()
    DiscordChannel1 = DiscordChannel["setChannel"]
    async with aiosqlite.connect('Studio.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT youtube_channel_id, discord_channel_id, enabled FROM discord_youtube WHERE id = ?", (guild_id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute(f"UPDATE discord_youtube SET youtube_channel_id = ?, discord_channel_id = ?, enabled =? WHERE id = ?", (YoutubeChannel1, DiscordChannel1, YoutubeEnabled1, guild_id,))
            else:
                await cursor.execute("INSERT INTO discord_youtube (youtube_channel_id, discord_channel_id, enabled, id) VALUES (?, ?, ?, ?)", (YoutubeChannel1, DiscordChannel1, YoutubeEnabled1, guild_id,))
        await db.commit()

    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

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
          
    TwitchEnabled = await request.get_json()
    TwitchEnabled1 = TwitchEnabled["isTwitchEnabled"]

    TwitchChannel = await request.get_json()
    TwitchChannel1 = TwitchChannel["setTwitch"]

    DiscordChannel = await request.get_json()
    DiscordChannel1 = DiscordChannel["setChannel"]
    async with aiosqlite.connect('Studio.db') as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT twitch_channel_id, discord_channel_id, enabled FROM discord_twitch WHERE id = ?", (guild_id,))
            data = await cursor.fetchone()
            if data:
                await cursor.execute(f"UPDATE discord_twitch SET twitch_channel_id = ?, discord_channel_id = ?, enabled =? WHERE id = ?", (TwitchChannel1, DiscordChannel1, TwitchEnabled1, guild_id,))
            else:
                await cursor.execute("INSERT INTO discord_twitch (twitch_channel_id, discord_channel_id, enabled, id) VALUES (?, ?, ?, ?)", (TwitchChannel1, DiscordChannel1, TwitchEnabled1, guild_id,))
        await db.commit()

    return await render_template("social.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

@app.route("/dashboard/<int:guild_id>/welcoming", methods=["POST"])
async def dashboardWelcomingPOST(guild_id):
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
   
    WelcomeEnabled = await request.get_json()
    WelcomeEnabled = WelcomeEnabled["isWelcomingEnabled"]

    WelcomeMessage = await request.get_json()
    WelcomeMessage = WelcomeMessage["setWelcome"]

    WelcomeChannel = await request.get_json()
    WelcomeChannel = WelcomeChannel["setChannel"]
    async with aiosqlite.connect('Studio.db') as db:
        async with db.cursor() as cursor:
                await cursor.execute("SELECT welcome_message, welcome_channel_id, welcome_enabled FROM guild_settings WHERE guild_id = ?", (guild_id,))
                data = await cursor.fetchone()
                if data:
                    await cursor.execute(f"UPDATE guild_settings SET welcome_message = ?, welcome_channel_id = ?, welcome_enabled =? WHERE guild_id = ?", (WelcomeMessage, WelcomeChannel, WelcomeEnabled, guild_id,))
                else:
                    await cursor.execute("INSERT INTO guild_settings (welcome_message, welcome_channel_id, welcome_enabled, guild_id) VALUES (?, ?, ?, ?)", (WelcomeMessage, WelcomeChannel, WelcomeEnabled, guild_id,))
        await db.commit()
        
    return await render_template("welcoming.html", guild=guild, guildName=guild_data["name"], guildID=guild_id, guildChannels=guild_data["channels"], guildIcon=guild_data["guildIcon"])

@app.route("/logout/")
async def logout():
    discord.revoke()
    return redirect(url_for("home"))

async def run_app():
    await app.run_task(port=3000)

async def run_client():
    await client.start('ODg5NDI5NTQyNTg0ODU2NjA3.GhQx4t.5JTsazooiGrsDdoeXw7zVwdUNkOgSzAteuQcXI')

youtube = build('youtube', 'v3', developerKey=config.YOUTUBEKEY)
conn = sqlite3.connect('studio.db')
c = conn.cursor()

@tasks.loop(minutes=1)
async def check_youtube():
    await asyncio.sleep(60)
    print("Running YT")
    c.execute('SELECT youtube_channel_id FROM discord_youtube')
    channel_ids = c.fetchall()
    for channel_id in channel_ids:
        search_response = youtube.search().list(
            channelId=channel_id,
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
            continue
        
        # Check if latest video ID is different from previous video ID for this channel
        c.execute('SELECT latest_video_id, discord_channel_id, failed_last_send, enabled FROM discord_youtube WHERE youtube_channel_id = ?', (channel_id,))
        row = c.fetchone()
        if row is not None:
            previous_video_id, discord_channel_id, failed_last_send, ytenabled = row
            if latest_video_id != previous_video_id:
                # Update latest video ID in the database
                c.execute('UPDATE discord_youtube SET latest_video_id = ? WHERE youtube_channel_id = ?', (latest_video_id, channel_id))
                conn.commit()
                if discord_channel_id and ytenabled == 'on':
                    # Post video in Discord channel
                    channel = client.get_channel(discord_channel_id)
                    await channel.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', channel_id))
                    conn.commit()
                else:
                    c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('True', channel_id))
                    conn.commit()
            else:
                if failed_last_send == 'True':
                    channel1 = client.get_channel(discord_channel_id)
                    if discord_channel_id is not None and ytenabled == 'on':
                        await channel1.send(f"{channel_name} Has Just Uploaded A Video! https://www.youtube.com/watch?v={latest_video_id}")
                        c.execute('UPDATE discord_youtube SET failed_last_send = ? WHERE youtube_channel_id = ?', ('False', channel_id))
                        conn.commit()
                    else:
                        continue
                else:
                    continue
        else:
            continue

@tasks.loop(minutes=1)
async def check_twitch():
    await asyncio.sleep(60)
    print("Running Twitch")
        # Replace with your client ID and secret
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET

    # Get list of channels from database
    ccursor = conn.execute("SELECT twitch_channel_id, is_live FROM discord_twitch")
    channel_info = ccursor.fetchall()

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
                            conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                            conn.commit()
                            cccursor = conn.execute(f"SELECT discord_channel_id, enabled FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                            discord_info, enabled = cccursor.fetchone()
                            if discord_info == 0 and enabled == 'on':
                                    # Post video in Discord channel
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_fake} Is Live Playing {game_name_fake}! {title_fake_fake} https://twitch.tv/{channel_name}")
                            else:
                                    continue
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
                                    conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                    conn.commit()
                                    cccursor = conn.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                    discord_info = cccursor.fetchone()
                                    if discord_info == 0:
                                        # Post video in Discord channel
                                        channel = client.get_channel(discord_info)
                                        await channel.send(f"{user_name} Is Live Playing {game_name}! {title_fake} https://twitch.tv/{channel_name}")
                                    else:
                                        continue
                        else:
                                continue
                    else:
                        continue
                except IndexError:
                    try:
                            title = req_data['data'][1]['title']
                            title
                            conn.execute(f"UPDATE discord_twitch SET is_live = 0 WHERE twitch_channel_id = '{channel_name}'")
                            conn.commit()
                    except IndexError:
                            game_name_real = req_data['data'][0]['game_name']
                            user_name_real = req_data['data'][0]['display_name']
                            title_real = req_data['data'][0]['title']
                            if not is_live:
                                # Update is_live column to True
                                conn.execute(f"UPDATE discord_twitch SET is_live = 1 WHERE twitch_channel_id = '{channel_name}'")
                                conn.commit()
                                cccursor = conn.execute(f"SELECT discord_channel_id FROM discord_twitch WHERE twitch_channel_id = '{channel_name}'")
                                discord_info = cccursor.fetchone()
                                if discord_info == 0:
                                    # Post video in Discord channel
                                    channel = client.get_channel(discord_info)
                                    await channel.send(f"{user_name_real} Is Live Playing {game_name_real}! {title_real} https://twitch.tv/{channel_name}")
                                else:
                                    continue
                            else:
                                continue

if __name__ == "__main__":
    loop = await asyncio.get_event_loop()
    tasks = [run_app(), run_client(), check_youtube(), check_twitch.start()]
    loop.run_until_complete(asyncio.gather(*tasks))