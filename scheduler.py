import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# スケジューラのインスタンス
scheduler = AsyncIOScheduler()

async def send_reminder(channel, content):
    """
    指定されたチャンネルにリマインダーを送信する関数
    """
    await channel.send(f"🔔 リマインダー: {content} の時間です！🔔")

def initialize_scheduler():
    """
    スケジューラを起動する関数
    """
    scheduler.start()
