# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    locales wget unzip curl software-properties-common \
    libnss3 libgconf-2-4 libxi6 libxrandr2 libxcomposite1 libasound2 \
    libxdamage1 libxtst6 fonts-liberation libappindicator3-1 xdg-utils \
    libu2f-udev chromium-driver && \
    apt-get clean

# ChromeDriver を /usr/local/bin に配置
RUN mv /usr/bin/chromedriver /usr/local/bin/chromedriver && chmod +x /usr/local/bin/chromedriver

# 環境変数の設定
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# ChromeDriver のパスを明示
ENV CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

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
