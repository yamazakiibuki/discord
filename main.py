import discord
import os
import sqlite3
import json
from keep import keep_alive

# データベースの初期化
def initialize_database():
    conn = sqlite3.connect('settings.db')  # データベースファイルを作成
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        bot_room_id INTEGER,
        announce_channel_ids TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_settings(guild_id, bot_room_id, announce_channel_ids):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO settings (guild_id, bot_room_id, announce_channel_ids)
    VALUES (?, ?, ?)
    ''', (guild_id, bot_room_id, json.dumps(announce_channel_ids)))
    conn.commit()
    conn.close()

def load_settings(guild_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT bot_room_id, announce_channel_ids FROM settings WHERE guild_id = ?', (guild_id,))
    row = c.fetchone()
    conn.close()
    if row:
        bot_room_id = row[0]
        announce_channel_ids = json.loads(row[1]) if row[1] else []
        return bot_room_id, announce_channel_ids
    else:
        return None, []

class MyClient(discord.Client):
    async def on_ready(self):
        print('Startup Success!!!')

    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        botRoomID = load_settings(guild_id)[0]

        # ボットルームが設定されていない場合は終了
        if botRoomID is None:
            print("ボットルームが設定されていません。")
            return

        botRoom = self.get_channel(botRoomID)
        if not botRoom or not isinstance(botRoom, discord.TextChannel):
            print("ボットルームが無効です。")
            return

        # チャンネルが変わったかどうかを確認して入退室のメッセージを送信
        if before.channel != after.channel:
            # チャネルから退出した場合
            if before.channel is not None and after.channel is None:
                await botRoom.send(f"**{before.channel.name}** から、__{member.name}__ が抜けました！")
                print(f"{member.name} が **{before.channel.name}** から抜けました。")

            # チャネルに参加した場合
            elif before.channel is None and after.channel is not None:
                await botRoom.send(f"**{after.channel.name}** に、__{member.name}__ が参加しました！")
                print(f"{member.name} が **{after.channel.name}** に参加しました。")

# Discordの権限を設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()

# データベースの初期化を実行
initialize_database()

client.run(os.environ['TOKEN'])
