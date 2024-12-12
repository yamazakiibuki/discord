# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# 更新・日本語化
RUN apt-get update && apt-get -y install locales && apt-get -y upgrade && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# 必要な依存関係（ChromeとChromeDriver）をインストール
RUN apt-get install -y wget unzip libxss1 libappindicator1 libindicator7 fonts-liberation libnss3 lsb-release \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y \
    && rm google-chrome-stable_current_amd64.deb \
    && wget https://chromedriver.storage.googleapis.com/$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# ChromeDriverに実行権限を付与
RUN chmod +x /usr/local/bin/chromedriver

# pip install
COPY requirements.txt /bot/
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# ポート開放 (FlaskやUvicornで指定したポート)
EXPOSE 8080

# 実行
CMD ["python", "main.py"]
