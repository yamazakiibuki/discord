import discord
import os
from datetime import datetime
from database import initialize_database, load_settings
from settings import set_channel
from vote import handle_question
from team import split_into_teams
from keep import keep_alive
from scheduler import initialize_scheduler, scheduler

class MyClient(discord.Client):
    async def on_ready(self):
        print('Startup Success!!!')
        initialize_scheduler()  # スケジューラの初期化

    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.content.startswith("!"):
            return

        command = message.content[1:].strip().split(".")

        if command[0] == "set_channel":
            await set_channel(command, message)
        elif command[0] == "question":
            await handle_question(command, message)
        elif command[0] == "team":
            if isinstance(message.author, discord.Member) and message.author.voice:
                voice_channel = message.author.voice.channel
                team_count = int(command[1]) if len(command) > 1 else 2  # デフォルトでチーム数2に設定
                teams, response = await split_into_teams(voice_channel, team_count)
                await message.channel.send(response)
            else:
                await message.channel.send("ボイスチャンネルに接続していません。")
        elif command[0] == "set_schedule":
            # スケジュールコマンドの処理
            if len(command) >= 4:
                date_str, time_str, content = command[1], command[2], " ".join(command[3:])
                try:
                    schedule_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    if schedule_time < datetime.now():
                        await message.channel.send("指定された日時は過去です。未来の日時を指定してください。")
                        return
                except ValueError:
                    await message.channel.send("日付や時刻の形式が正しくありません。例: !set_schedule 2024-12-25 15:00 イベント")
                    return

                await message.channel.send(f"予定が設定されました！\n日時: {schedule_time}\n内容: {content}")
                scheduler.add_job(self.send_reminder, "date", run_date=schedule_time, args=[message.channel, content])
            else:
                await message.channel.send("コマンド形式が正しくありません。例: !set_schedule 2024-12-25 15:00 イベント")
        else:
            await message.channel.send("無効なコマンドです。")

    async def send_reminder(self, channel, content):
        await channel.send(f"🔔 リマインダー: {content} の時間です！🔔")

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
initialize_database()

# Bot実行
client.run(os.environ['TOKEN'])
