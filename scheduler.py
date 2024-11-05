import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime

# スケジューラのインスタンス
scheduler = AsyncIOScheduler()

async def send_reminder(channel, content):
    """
    指定されたチャンネルにリマインダーを送信する関数
    """
    await channel.send(f"🔔 リマインダー: {content} の時間です！🔔")

async def set_schedule(channel, date: str, time: str, content: str):
    """
    リマインダーを設定するコマンド
    例: !set_schedule 2024-12-25 15:00 クリスマスイベント
    """
    # 日時の解析
    try:
        schedule_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        if schedule_time < datetime.now():
            await channel.send("指定された日時は過去です。未来の日時を指定してください。")
            return
    except ValueError:
        await channel.send("日付や時刻の形式が正しくありません。例: !set_schedule 2024-12-25 15:00 クリスマスイベント")
        return

    # リマインダーの設定
    await channel.send(f"予定が設定されました！\n日時: {schedule_time}\n内容: {content}")
    scheduler.add_job(send_reminder, DateTrigger(run_date=schedule_time), args=[channel, content])

def initialize_scheduler():
    """
    スケジューラを起動する関数
    """
    scheduler.start()
