import requests
from bs4 import BeautifulSoup
import discord
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def search_yahoo_news(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=r'C:\chromedriver-win64\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        search_url = f"https://news.yahoo.co.jp/search?p={query}"
        driver.get(search_url)

        articles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.sc-1u4589e-0.kKmBYF'))
        )[:3]

        if not articles:
            return "該当する記事が見つかりませんでした。"

        message = f"**Yahoo!ニュース 検索結果**：{query}\n\n"
        for i, article in enumerate(articles, 1):
            try:
                title = article.find_element(By.CSS_SELECTOR, 'div.sc-3ls169-0.sc-110wjhy-2.dHAJpi.dKognN').text
                link = article.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                message += f"{i}. [{title}]({link})\n"
            except Exception as e:
                print(f"記事取得中にエラーが発生: {e}")
                continue

        return message
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"
    finally:
        driver.quit()
