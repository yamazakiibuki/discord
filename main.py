import discord
import os
from datetime import datetime
from database import initialize_database, load_settings
from settings import set_channel, handle_channel_setup
from vote import handle_question_navigation, list_votes, delete_vote
from team import split_into_teams
from keep import keep_alive
from scheduler import initialize_scheduler


class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.temporary_settings = {}  # ユーザーごとの設定進行状況を管理

    async def on_ready(self):
        print('Startup Success!!!')
        initialize_scheduler()
        initialize_database()

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id in self.temporary_settings:
            # 設定進行中ならコマンド形式を問わず処理
            await handle_channel_setup(message, self.temporary_settings)
            return
        
        if not message.content.startswith("!"):
            return

        command = message.content[1:].strip().split(" ")

        if command[0] == "set_channel":
            await set_channel(message, self.temporary_settings)
            print("DEBUG: set_channel を呼び出しました")
        elif message.author.id in self.temporary_settings:
            # 現在進行中の設定がある場合
            await handle_channel_setup(message, self.temporary_settings)
            print("DEBUG: handle_channel_setup を呼び出しました")
        elif command[0] == "question":
            await handle_question_navigation(command, message, self)
        elif command[0] == "list_votes":
            await list_votes(message)
        elif command[0] == "delete_vote":
            await delete_vote(command, message)
        elif command[0] == "team":
            await self.handle_team_command(command, message)
        elif command[0] == "set_schedule":
            await self.start_schedule_navigation(message)
        else:
            await message.channel.send("無効なコマンドです。")

    async def handle_team_command(self, command, message):
        if isinstance(message.author, discord.Member) and message.author.voice:
            voice_channel = message.author.voice.channel
            team_count = int(command[1]) if len(command) > 1 else 2
            teams, response = await split_into_teams(voice_channel, team_count)
            await message.channel.send(response)
        else:
            await message.channel.send("ボイスチャンネルに接続していません。")

    async def start_schedule_navigation(self, message):
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
        try:
            schedule_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if schedule_time < datetime.now():
                await channel.send("指定された日時は過去です。未来の日時を指定してください。")
                return
        except ValueError:
            await channel.send("日付や時刻の形式が正しくありません。例: 2024-12-25 15:00")
            return

        await channel.send(f"予定が設定されました！\n日時: {schedule_time}\n内容: {content}")

    async def on_member_join(self, member):
        try:
            await member.send(f"ようこそ、{member.name}さん！サーバーへようこそ！私はゲームボットです。")
            print(f"Sent welcome message to {member.name}")
        except Exception as e:
            print(f"Could not send message to {member.name}: {e}")

async def on_voice_state_update(self, member, before, after):
    try:
        settings = load_settings(member.guild.id)
        if not settings:
            print(f"Settings not found for guild ID {member.guild.id}")
            return

        bot_room_id, announce_channel_ids = settings
        if before.channel and before.channel.id == bot_room_id and not after.channel:
            for channel_id in announce_channel_ids:
                announce_channel = self.get_channel(channel_id)
                if announce_channel:
                    await announce_channel.send(f"**{before.channel.name}** から、__{member.name}__ が抜けました！")
        elif after.channel and after.channel.id == bot_room_id and not before.channel:
            for channel_id in announce_channel_ids:
                announce_channel = self.get_channel(channel_id)
                if announce_channel:
                    await announce_channel.send(f"**{after.channel.name}** に、__{member.name}__ が参加しました！")
    except Exception as e:
        print(f"Error in on_voice_state_update: {e}")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()

if 'TOKEN' not in os.environ:
    print("Error: Discord bot token not found in environment variables.")
else:
    client.run(os.environ['TOKEN'])
