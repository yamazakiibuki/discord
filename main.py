import discord
import os
import sqlite3
import json
import asyncio
import random
from keep import keep_alive

# データベースの初期化
def initialize_database():
    conn = sqlite3.connect('settings.db')
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

# 設定を保存する関数
def save_settings(guild_id, bot_room_id, announce_channel_ids):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO settings (guild_id, bot_room_id, announce_channel_ids)
    VALUES (?, ?, ?)
    ''', (guild_id, bot_room_id, json.dumps(announce_channel_ids)))
    conn.commit()
    conn.close()

# 設定を読み込む関数
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

# チーム分け機能クラス
class TeamDivider:
    def __init__(self):
        self.channel_mem = []
        self.mem_len = 0
        self.vc_state_err = '実行できません。ボイスチャンネルに入ってコマンドを実行してください。'

    def set_mem(self, ctx):
        state = ctx.author.voice
        if state is None:
            return False
        self.channel_mem = [i.name for i in state.channel.members]
        self.mem_len = len(self.channel_mem)
        return True

    def make_party_num(self, ctx, party_num):
        if not self.set_mem(ctx):
            return self.vc_state_err
        if party_num > self.mem_len or party_num <= 0:
            return '実行できません。チーム数が適切か確認してください。'
        random.shuffle(self.channel_mem)
        teams = [self.channel_mem[i::party_num] for i in range(party_num)]
        team_msg = ''
        for i, team in enumerate(teams, start=1):
            team_msg += f'チーム {i}: {", ".join(team)}\n'
        return team_msg

# 投票用のリアクション絵文字
list_yesno = ['🙆‍♂️', '🙅‍♂️']
list_vote = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

# クライアントクラス
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team_divider = TeamDivider()

    async def on_ready(self):
        print('Startup Success!!!')

    async def on_message(self, message):
        if message.author.bot:
            return

        command = message.content.split(".")

        # チーム分けコマンド
        if command[0] == "team":
            if len(command) < 2:
                await message.channel.send("チーム数を指定してください。使用法: `team.[チーム数]`")
                return
            try:
                num_teams = int(command[1])
                result = self.team_divider.make_party_num(message, num_teams)
                await message.channel.send(result)
            except ValueError:
                await message.channel.send("チーム数には整数を指定してください。")

        # チャンネル設定コマンド
        elif command[0] == "set_channel":
            # ...（既存の set_channel コマンドの処理）...

        # 投票関連のコマンド
        elif command[0] == "question":
            # ...（既存の question コマンドの処理）...

    async def on_member_join(self, member):
        try:
            await member.send(f"ようこそ、{member.name}さん！サーバーへようこそ！私はゲームボットです。あなたの快適なゲームライフをサポートします！")
            print(f"Sent welcome message to {member.name}")
        except Exception as e:
            print(f"Could not send message to {member.name}: {e}")

    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        botRoomID = load_settings(guild_id)[0]
        if botRoomID is not None:
            botRoom = self.get_channel(botRoomID)
            if botRoom is None or not isinstance(botRoom, discord.TextChannel):
                print("ボットルームが設定されていません。")
                return
            if before.channel == after.channel:
                return
            if before.channel is not None and after.channel is None:
                await botRoom.send(f"**{before.channel.name}** から、__{member.name}__ が抜けました！")
            elif before.channel is None and after.channel is not None:
                await botRoom.send(f"**{after.channel.name}** に、__{member.name}__ が参加しました！")

# Discordの権限を設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()
initialize_database()
client.run(os.environ['TOKEN'])
