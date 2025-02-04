# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    locales wget unzip curl software-properties-common \
    libnss3 libgconf-2-4 libxi6 libxrandr2 libxcomposite1 libasound2 \
    libxdamage1 libxtst6 fonts-liberation libappindicator3-1 xdg-utils \
    libu2f-udev ca-certificates \
    google-chrome-stable && \
    apt-get clean

# ChromeDriver をインストール
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/bin/chromedriver

# 環境変数の設定
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# ChromeDriver のパスを明示
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# Pythonのパッケージをインストール
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# SHM サイズを増やす (Chrome のクラッシュ対策)
RUN mkdir -p /dev/shm && chmod 1777 /dev/shm

# ポート開放
EXPOSE 8080

# 実行
ENTRYPOINT ["python", "main.py"]
