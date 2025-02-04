# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    locales wget unzip curl software-properties-common \
    libnss3 libgconf-2-4 libxi6 libxrandr2 libxcomposite1 libasound2 \
    libxdamage1 libxtst6 fonts-liberation libappindicator3-1 xdg-utils \
    libu2f-udev ca-certificates gnupg && \
    apt-get clean

# Google Chrome のリポジトリを追加
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean

# ChromeDriver をインストール（修正）
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/bin/chromedriver

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
