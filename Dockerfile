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

# ChromeDriverのインストール
RUN apt-get install -y wget unzip \
    && wget https://chromedriver.storage.googleapis.com/131.0.6778.108/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip

# pip install
COPY requirements.txt /bot/
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# ポート開放 (FlaskやUvicornで指定したポート)
EXPOSE 8080

# 実行
CMD ["python", "main.py"]
