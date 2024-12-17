import asyncio
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ログ設定
logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s %(levelname)s: %(message)s")

# イベントループの取得
loop = asyncio.get_event_loop()

# 同期関数: Seleniumを使用してYahoo!ニュースを検索する
def fetch_news_sync(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード
    chrome_options.add_argument("--no-sandbox")  # サンドボックス無効化
    chrome_options.add_argument("--disable-dev-shm-usage")  # 共有メモリの制限回避
    chrome_options.add_argument("--disable-gpu")  # GPU使用を無効化

    service = Service(executable_path="/usr/bin/chromedriver")  # ChromeDriverのパス
    driver = None
    results = []

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        search_url = f"https://news.yahoo.co.jp/search?p={query}"
        driver.get(search_url)

        # ニュース記事の要素を取得（上位3件）
        articles = driver.find_elements(By.CSS_SELECTOR, "li.sc-1u4589e-0")[:3]
        for article in articles:
            try:
                title = article.find_element(By.CSS_SELECTOR, "div.sc-3ls169-0").text
                link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                results.append((title, link))
            except Exception:
                continue

    except Exception as e:
        logging.error(f"エラーが発生しました: {str(e)}\n詳細:\n{traceback.format_exc()}")
    finally:
        if driver:
            driver.quit()
    return results

# 非同期関数: Discord上でニュース検索を行う
async def yahoo_news_search(ctx, query):
    try:
        # 同期処理を非同期タスクとして実行
        results = await loop.run_in_executor(None, fetch_news_sync, query)
        
        # 検索結果がない場合
        if not results:
            await ctx.send("該当する記事が見つかりませんでした。")
            return

        # 検索結果の整形
        message = f"**Yahoo!ニュース 検索結果**：{query}\n\n"
        for i, (title, link) in enumerate(results, 1):
            message += f"{i}. [{title}]({link})\n"

        # Discordメッセージ分割送信
        max_length = 2000  # Discordの1メッセージの最大文字数
        for i in range(0, len(message), max_length):
            await ctx.send(message[i:i + max_length])

    except Exception as e:
        # エラー内容をログに記録
        error_details = traceback.format_exc()
        logging.error(f"エラーが発生しました: {str(e)}\n詳細:\n{error_details}")
        
        # Discordに簡潔なエラーメッセージを送信
        truncated_message = str(e)[:1500] + "..." if len(str(e)) > 1500 else str(e)
        await ctx.send(f"エラーが発生しました。詳細: {truncated_message}\n管理者にお問い合わせください。")
