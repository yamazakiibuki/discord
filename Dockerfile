# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# システムの更新 & 日本語設定
RUN apt-get update && apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    apt-get -y install wget unzip curl software-properties-common && \
    apt-get -y install libnss3 libgconf-2-4 libxi6 libxrandr2 libxcomposite1 libasound2 libxdamage1 libxtst6 \
                       fonts-liberation libappindicator3-1 xdg-utils libu2f-udev && \
    apt-get -y install chromium-driver && \
    mv /usr/bin/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# 環境変数の設定
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# ChromeDriver のパスを明示
ENV CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# Python環境の準備
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# ChromeDriverとChromiumのバージョン確認スクリプト
RUN echo 'chromedriver --version && chromium --version' > /bot/test_chromedriver.sh && chmod +x /bot/test_chromedriver.sh

# ポート開放 (FlaskやUvicornを使用する場合)
EXPOSE 8080

# 実行
ENTRYPOINT ["python", "main.py"]
