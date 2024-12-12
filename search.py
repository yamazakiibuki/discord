from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

# ログ設定
logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s %(levelname)s: %(message)s")

async def yahoo_news_search(ctx, query):
    # Chromeドライバーの設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    service = Service(executable_path="/usr/bin/chromedriver")  # Linux用のドライバパス

    driver = None
    try:
        # WebDriverの起動
        driver = webdriver.Chrome(service=service, options=chrome_options)
        search_url = f"https://news.yahoo.co.jp/search?p={query}"
        driver.get(search_url)

        # ニュース記事を取得（上位3件）
        articles = driver.find_elements(By.CSS_SELECTOR, "li.sc-1u4589e-0")[:3]
        if not articles:
            await ctx.send("該当する記事が見つかりませんでした。")
            return

        # 検索結果を整形
        message = f"**Yahoo!ニュース 検索結果**：{query}\n\n"
        for i, article in enumerate(articles, 1):
            try:
                title = article.find_element(By.CSS_SELECTOR, "div.sc-3ls169-0").text
                link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                message += f"{i}. [{title}]({link})\n"
            except Exception:
                continue

        # メッセージが長い場合は分割して送信
        max_length = 2000  # Discordの制限
        for i in range(0, len(message), max_length):
            await ctx.send(message[i:i+max_length])

    except Exception as e:
        # エラー内容をログに記録
        error_details = traceback.format_exc()
        logging.error(f"エラーが発生しました: {str(e)}\n詳細:\n{error_details}")
        
        # Discordに簡潔なエラーメッセージを送信
        truncated_message = str(e)[:1500] + "..." if len(str(e)) > 1500 else str(e)
        await ctx.send(f"エラーが発生しました。詳細: {truncated_message}\n管理者にお問い合わせください。")

    finally:
        if driver:
            driver.quit()
