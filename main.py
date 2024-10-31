import discord
import os
from database import initialize_database, load_settings
from settings import set_channel
from vote import handle_question
from team import split_into_teams  # team.pyからチーム分け機能をインポート
from keep import keep_alive

class MyClient(discord.Client):
    async def on_ready(self):
        print('Startup Success!!!')

    async def on_message(self, message):
        if message.author.bot:
            return
        command = message.content.split(".")

        # コマンドの分岐処理
        if command[0] == "set_channel":
            await set_channel(command, message)
        elif command[0] == "question":
            await handle_question(command, message)
        elif command[0] == "team":
            # チーム分けコマンド
            voice_channel = message.author.voice.channel if message.author.voice else None
            if voice_channel:
                team_count = int(command[1]) if len(command) > 1 else 2  # デフォルトでチーム数2に設定
                teams, response = await split_into_teams(voice_channel, team_count)
                await message.channel.send(response)
            else:
                await message.channel.send("ボイスチャンネルに接続していません。")
        else:
            await message.channel.send("無効なコマンドです。")

    async def on_member_join(self, member):
        try:
            await member.send(f"ようこそ、{member.name}さん！サーバーへようこそ！私はゲームボットです。")
            print(f"Sent welcome message to {member.name}")
        except Exception as e:
            print(f"Could not send message to {member.name}: {e}")

    async def on_voice_state_update(self, member, before, after):
        botRoomID = load_settings(member.guild.id)[0]
        botRoom = self.get_channel(botRoomID) if botRoomID else None

        if botRoom and before.channel != after.channel:
            if before.channel and not after.channel:
                await botRoom.send(f"**{before.channel.name}** から、__{member.name}__ が抜けました！")
            elif not before.channel and after.channel:
                await botRoom.send(f"**{after.channel.name}** に、__{member.name}__ が参加しました！")

# BotのIntent設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()
initialize_database()

# Botの実行
client.run(os.environ['TOKEN'])
