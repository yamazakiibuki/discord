# ベースイメージの指定
FROM python:3.12.3

# 作業ディレクトリの設定
WORKDIR /bot

# 更新・日本語化
RUN apt-get update && apt-get -y install locales && apt-get -y upgrade && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 && \
    apt-get -y install wget unzip curl software-properties-common && \
    apt-get -y install libnss3 libgconf-2-4 libxi6 libxrandr2 libxcomposite1 libasound2 libxdamage1 libxtst6 fonts-liberation libappindicator3-1 xdg-utils libu2f-udev && \
    apt-get -y install chromium chromium-driver

# 環境変数の設定
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ Asia/Tokyo
ENV TERM xterm

# pip install
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# ポート開放 (FlaskやUvicornで指定したポート)
EXPOSE 8080

# 実行
CMD ["python", "main.py"]
