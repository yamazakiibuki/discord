from apscheduler.schedulers.asyncio import AsyncIOScheduler

# スケジューラのインスタンス
scheduler = AsyncIOScheduler()

def initialize_scheduler():
    """
    スケジューラを起動する関数（既に起動済みならスキップ）
    """
    if not scheduler.running:
        scheduler.start()
