import sqlite3
import config
from nextcord.ext import tasks

conn = sqlite3.connect('discord_youtube.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS discord_youtube
                (server_name, discord_channel_id integer, youtube_channel_id text, latest_video_id text, failed_last_send text, id integer)''')
conn.commit()

def add_id():
    c.execute('ALTER TABLE `discord_youtube` ADD `id` INTEGER AUTO_INCREMENT NOT NULL;')
    conn.commit()

#add_id()


def discord():
    discord_id_blacklist = []
    with open('discord.txt', 'r') as f:
        discord_ids = f.readlines()
        for discord_channel_id in discord_ids:
                discord_channel_id_clean = discord_channel_id.strip()
                c.execute('SELECT discord_channel_id FROM discord_youtube')
                existing_discord_channel = c.fetchall()
                for id in existing_discord_channel:
                    if discord_channel_id_clean == id:
                        print(f"{discord_channel_id_clean} already added, skipping")
                        continue
                    else:
                        if discord_channel_id_clean in discord_id_blacklist:
                            continue
                        else:
                            print(discord_id_blacklist)
                            c.execute('SELECT discord_channel_id FROM discord_youtube')
                            stuff_there = c.fetchall()
                            #c.execute('UPDATE discord_youtube SET discord_channel_id = ?', (discord_channel_id_clean,))
                            c.execute('INSERT INTO discord_youtube (discord_channel_id) VALUES (?)', (discord_channel_id_clean,))
                            conn.commit()
                            discord_id_blacklist.append(discord_channel_id_clean)
                            print(f"Added {discord_channel_id_clean}")
                            '''if existing_discord_channel == discord_channel_id:
                                                print(f"Discord ID already set for {discord_channel_id}, skipping")
                                                continue
                                            else:
                                                c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE id = ?', (discord_channel_id, row_id,))
                                                conn.commit()
                                                print(f"Added {discord_channel_id} for {yt_channel_id}")'''
def youtube():
    global_discord_id_blacklist = []
    with open('youtube.txt', 'r') as f:
        yt_ids = f.readlines()
        for yt_channel_id in yt_ids:
            yt_channel_id = yt_channel_id.strip()
            c.execute('SELECT id, youtube_channel_id, discord_channel_id FROM discord_youtube WHERE youtube_channel_id = ?', (yt_channel_id,))
            existing_channel = c.fetchone()
            if existing_channel:
                row_id, exsisting_youtube_channel_id, existing_discord_channel_id = existing_channel
                if exsisting_youtube_channel_id:
                    continue
            else:
                row_id = c.lastrowid
                new_row_id = row_id + 1
                c.execute('INSERT INTO discord_youtube (youtube_channel_id) VALUES (?)', (yt_channel_id,))
                c.execute('UPDATE discord_youtube SET id = ? WHERE youtube_channel_id = ?', (new_row_id, yt_channel_id,))
                conn.commit()
                row_id = c.lastrowid
                with open('discord.txt', 'r') as f:
                    discord_ids = f.readlines()
                    the = False
                    discord_id_blacklist = []
                    for discord_channel_id in discord_ids:
                            discord_channel_id_clean = discord_channel_id.strip()
                            if discord_channel_id_clean in global_discord_id_blacklist:
                                    continue
                            elif discord_channel_id_clean in discord_id_blacklist:
                                    break
                            elif discord_channel_id_clean == id:
                                    break
                            else:
                                    c.execute('UPDATE discord_youtube SET discord_channel_id = ? WHERE youtube_channel_id = ?', (discord_channel_id_clean, yt_channel_id,))
                                    conn.commit()
                                    global_discord_id_blacklist.append(discord_channel_id_clean)
                                    for discord_id in discord_ids:
                                        stri = discord_id.strip()
                                        discord_id_blacklist.append(stri)
                                    the = True
                                    local_string = discord_id_blacklist
                                    global_string = global_discord_id_blacklist
                                    #print(f'Local Blacklist: {local_string}') ##DEBUG COMMAND
                                    #print(f'Global Blacklist: {global_string}') ##DEBUG COMMAND
                                    break

youtube()