from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

async def yahoo_news_search(ctx, query):
    # Chromeドライバーの設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path="./bin/chromedriver.exe")

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        search_url = f"https://news.yahoo.co.jp/search?p={query}"
        driver.get(search_url)

        # ニュース記事を取得 (上位3件)
        articles = driver.find_elements(By.CSS_SELECTOR, "li.sc-1u4589e-0")[:3]
        if not articles:
            await ctx.send("該当する記事が見つかりませんでした。")
            return

        message = f"**Yahoo!ニュース 検索結果**：{query}\n\n"
        for i, article in enumerate(articles, 1):
            try:
                title = article.find_element(By.CSS_SELECTOR, "div.sc-3ls169-0").text
                link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                message += f"{i}. [{title}]({link})\n"
            except Exception:
                continue

        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {str(e)}")
    finally:
        if driver:
            driver.quit()
