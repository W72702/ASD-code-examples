#############################################################################################
# This is code I was using to update databases (hence the name)                             #
# If you want to run this you should be able to simply run it                               #
# I have added comments to the code any comment starting with ######## is a comment from me #
#############################################################################################

import sqlite3
import config
from nextcord.ext import tasks

######## Connect to a database ########
conn = sqlite3.connect('discord_youtube.db')
c = conn.cursor()

######## Create a table if one doesnt exsists already ########
c.execute('''CREATE TABLE IF NOT EXISTS discord_youtube
                (server_name, discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text, id integer)''')
conn.commit()

######## Old code that added a new row to the table ########
#def add_id():
#    c.execute('ALTER TABLE `discord_youtube` ADD `id` INTEGER AUTO_INCREMENT NOT NULL;')
#    conn.commit()

#add_id()

######## This is more of that discord youtube stuff here we see old code for the discord function ########
#def discord():
#    discord_id_blacklist = []
#    with open('discord.txt', 'r') as f:
#        discord_ids = f.readlines()
#        for discord_channel_id in discord_ids:
#                discord_channel_id_clean = discord_channel_id.strip()
#                c.execute('SELECT discord_channel_id FROM discord_youtube')
#                existing_discord_channel = c.fetchall()
#                for id in existing_discord_channel:
#                    if discord_channel_id_clean == id:
#                        print(f"{discord_channel_id_clean} already added, skipping")
#                        continue
#                    else:
#                       if discord_channel_id_clean in discord_id_blacklist:
#                            continue
#                        else:
#                            print(discord_id_blacklist)
#                            c.execute('SELECT discord_channel_id FROM discord_youtube')
#                            stuff_there = c.fetchall()
#                            #c.execute('UPDATE discord_youtube SET discord_channel_id = ?', (discord_channel_id_clean,))
#                            c.execute('INSERT INTO discord_youtube (discord_channel_id) VALUES (?)', (discord_channel_id_clean,))
#                            conn.commit()
#                            discord_id_blacklist.append(discord_channel_id_clean)
#                            print(f"Added {discord_channel_id_clean}")
#                            '''if existing_discord_channel == discord_channel_id:
#                                                print(f"Discord ID already set for {discord_channel_id}, skipping")
#                                                continue
#                                            else:
#                                                c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE id = ?', (discord_channel_id, row_id,))
#                                                conn.commit()
#                                                print(f"Added {discord_channel_id} for {yt_channel_id}")'''

######## Here is the youtube command ########
def youtube():
  ######## We set a global discord channel id blacklist ########
    global_discord_id_blacklist = []
    ######## Open the file with our youtube channel ids and then add them to a list ########
    with open('youtube.txt', 'r') as f:
        yt_ids = f.readlines()
        ######## For each youtube channel in that list check if it exsists in the database already continue ########
        for yt_channel_id in yt_ids:
            yt_channel_id = yt_channel_id.strip()
            c.execute('SELECT id, youtube_channel_id, discord_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (yt_channel_id,))
            existing_channel = c.fetchone()
            if existing_channel:
                row_id, exsisting_youtube_channel_id, existing_discord_channel_id = existing_channel
                if exsisting_youtube_channel_id:
                    continue
            ######## Else get the last row id and then add 1 to it ########
            else:
                row_id = c.lastrowid
                new_row_id = row_id + 1
                ######## Add the youtube channel into the database with the row id ########
                c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (yt_channel_id,))
                c.execute('UPDATE discord_youtube SET id = ? WHERE youtube_channel_id = ?', (new_row_id, yt_channel_id,))
                conn.commit()
                ######## Set the new row id ########
                row_id = c.lastrowid
                ######## Open the file with our discord channels in it and write them to a list ########
                with open('discord.txt', 'r') as f:
                    discord_ids = f.readlines()
                    ######## Set the to false ########
                    the = False
                    ######## Create a local discord channel id blacklist ########
                    discord_id_blacklist = []
                    ######## For every discord channel id in the list strip it so its just the id ########
                    for discord_channel_id in discord_ids:
                            discord_channel_id_clean = discord_channel_id.strip()
                            ######## If the id is in the global blacklist then skip it ########
                            if discord_channel_id_clean in global_discord_id_blacklist:
                                    continue
                            ######## If its in the local blacklist skip it ########
                            elif discord_channel_id_clean in discord_id_blacklist:
                                    break
                            ######## I actually dont remember what this did but its here ########
                            elif discord_channel_id_clean == id:
                                    break
                            ######## Else add the discord channel to the database ########
                            else:
                                    c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel_id_clean, yt_channel_id,))
                                    conn.commit()
                                  ######## Add the id to the global blacklist ########
                                    global_discord_id_blacklist.append(discord_channel_id_clean)
                                    ######## For each id in the list above then add it to the local blacklist ########
                                    for discord_id in discord_ids:
                                        stri = discord_id.strip()
                                        discord_id_blacklist.append(stri)
                                    ######## The is now true ########
                                    the = True
                                    ######## BREAK ########
                                    break
######## Run this mess i just commented ########
youtube()
