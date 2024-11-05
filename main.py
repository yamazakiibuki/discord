import discord
import os
from datetime import datetime
from database import initialize_database, load_settings
from settings import set_channel
from vote import handle_question_navigation, list_votes, delete_vote  # 修正
from team import split_into_teams
from keep import keep_alive
from scheduler import initialize_scheduler

class MyClient(discord.Client):
    async def on_ready(self):
        print('Startup Success!!!')
        initialize_scheduler()  # スケジューラの初期化
        initialize_database()   # データベースの初期化

    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.content.startswith("!"):
            return

        command = message.content[1:].strip().split(".")

        if command[0] == "set_channel":
            await set_channel(command, message)
        elif command[0] == "question":
            await handle_question_navigation(command, message, self)  # handle_question_navigationを使用
        elif command[0] == "list_votes":
            await list_votes(message)
        elif command[0] == "delete_vote":
            await delete_vote(command, message)
        elif command[0] == "team":
            if isinstance(message.author, discord.Member) and message.author.voice:
                voice_channel = message.author.voice.channel
                team_count = int(command[1]) if len(command) > 1 else 2  # デフォルトでチーム数2に設定
                teams, response = await split_into_teams(voice_channel, team_count)
                await message.channel.send(response)
            else:
                await message.channel.send("ボイスチャンネルに接続していません。")
        elif command[0] == "set_schedule":
            await self.start_schedule_navigation(message)
        else:
            await message.channel.send("無効なコマンドです。")

    async def start_schedule_navigation(self, message):
        """スケジュール設定のナビゲーションを開始する"""
        await message.channel.send("スケジュール設定を始めます。最初に日付を入力してください（例: 2024-12-25）。")

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            date_msg = await self.wait_for('message', check=check, timeout=60.0)
            date_str = date_msg.content

            await message.channel.send("次に時間を入力してください（例: 15:00）。")
            time_msg = await self.wait_for('message', check=check, timeout=60.0)
            time_str = time_msg.content

            await message.channel.send("最後に内容を入力してください。")
            content_msg = await self.wait_for('message', check=check, timeout=60.0)
            content = content_msg.content

            await self.set_schedule(message.channel, date_str, time_str, content)

        except discord.TimeoutError:
            await message.channel.send("タイムアウトしました。再度コマンドを実行してください。")

    async def set_schedule(self, channel, date_str, time_str, content):
        """スケジュールを設定する"""
        try:
            schedule_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if schedule_time < datetime.now():
                await channel.send("指定された日時は過去です。未来の日時を指定してください。")
                return
        except ValueError:
            await channel.send("日付や時刻の形式が正しくありません。例: !set_schedule 2024-12-25 15:00 イベント")
            return

        await channel.send(f"予定が設定されました！\n日時: {schedule_time}\n内容: {content}")

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

# Intent設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

# Botのインスタンス
client = MyClient(intents=intents)
keep_alive()
initialize_database()  # データベースの初期化

# Bot実行
client.run(os.environ['TOKEN'])
