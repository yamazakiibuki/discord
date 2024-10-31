import discord
import os
import sqlite3
import json
import random
from keep import keep_alive

# データベースの初期化
def initialize_database():
    conn = sqlite3.connect('settings.db')  # データベースファイルを作成
    c = conn.cursor()

    # テーブル作成
    c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        bot_room_id INTEGER,
        announce_channel_ids TEXT
    )
    ''')
    conn.commit()
    conn.close()

# 設定を保存する関数
def save_settings(guild_id, bot_room_id, announce_channel_ids):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()

    # アナウンスチャンネルIDsをJSON形式で保存
    c.execute('''
    INSERT OR REPLACE INTO settings (guild_id, bot_room_id, announce_channel_ids)
    VALUES (?, ?, ?)
    ''', (guild_id, bot_room_id, json.dumps(announce_channel_ids)))
    conn.commit()
    conn.close()

# 設定を読み込む関数
def load_settings(guild_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()

    c.execute('SELECT bot_room_id, announce_channel_ids FROM settings WHERE guild_id = ?', (guild_id,))
    row = c.fetchone()
    conn.close()

    if row:
        bot_room_id = row[0]
        announce_channel_ids = json.loads(row[1]) if row[1] else []
        return bot_room_id, announce_channel_ids
    else:
        return None, []

# 投票用のリアクション絵文字
list_yesno = ['🙆‍♂️', '🙅‍♂️']
list_vote = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

def emphasize(text):
    return "**" + text + "**"

def underline(text):
    return "__" + text + "__"

def isContainedNoInput(command):
    return any(i == '' for i in command)

class DiscordBot:
    def __init__(self):
        self.channel_mem = []
        self.mem_len = 0
        self.vc_state_err = '実行できません。ボイスチャンネルに入ってコマンドを実行してください。'

    def set_mem(self, ctx):
        state = ctx.author.voice  # コマンド実行者のVCステータスを取得
        if state is None:
            return False

        self.channel_mem = [i.name for i in state.channel.members]  # VCメンバリスト取得
        self.mem_len = len(self.channel_mem)  # 人数取得
        return True

    # チーム数を指定した場合のチーム分け
    def make_party_num(self, ctx, party_num):
        team = []
        remainder = []

        if self.set_mem(ctx) is False:
            return self.vc_state_err

        # 指定数の確認
        if party_num > self.mem_len or party_num <= 0:
            return '実行できません。チーム分けできる数を指定してください。(チーム数を指定しない場合は、デフォルトで2が指定されます)'

        # メンバーリストをシャッフル
        random.shuffle(self.channel_mem)

        # チーム分け
        for i in range(party_num):
            team.append("=====チーム" + str(i + 1) + "=====")
            team.extend(self.channel_mem[i::party_num])

        return '\n'.join(team)

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.discord_bot = DiscordBot()  # DiscordBotクラスのインスタンスを作成

    async def on_ready(self):
        print('Startup Success!!!')

    async def on_message(self, message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return

        # コマンドのセパレータは"."
        command = message.content.split(".")

        # チャンネル設定コマンド
        if command[0] == "set_channel":
            if len(command) < 3:
                await message.channel.send("チャンネル名を指定してください。使用法: `set_channel.[BOT_ROOM|ANNOUNCE_CHANNEL].[CHANNEL_NAME]`")
                return

            channel_type = command[1]
            channel_name = command[2]
            guild_id = message.guild.id

            channel = discord.utils.get(message.guild.channels, name=channel_name)
            if channel is None:
                await message.channel.send("指定されたチャンネル名が見つかりません。")
                return

            if channel_type == "BOT_ROOM":
                save_settings(guild_id, channel.id, load_settings(guild_id)[1])  # 既存のアナウンスチャンネルIDを保持
                await message.channel.send(f"ボットルームを `{channel.name}` に設定しました。")
            elif channel_type == "ANNOUNCE_CHANNEL":
                _, announce_channel_ids = load_settings(guild_id)
                announce_channel_ids.append(channel.id)
                save_settings(guild_id, load_settings(guild_id)[0], announce_channel_ids)
                await message.channel.send(f"アナウンスチャンネルを `{channel.name}` に設定しました。")
            else:
                await message.channel.send("チャンネルタイプが無効です。`BOT_ROOM` または `ANNOUNCE_CHANNEL` を指定してください。")

        # 投票関連のコマンド
        elif command[0] == "question":
            try:
                # Yes-No 疑問文
                if command[1] == "yes-no":
                    embed = discord.Embed(title=command[2], description="", color=discord.Colour.blue())
                    voting_msg = await message.channel.send(embed=embed)
                    for i in range(len(list_yesno)):
                        await voting_msg.add_reaction(list_yesno[i])
                    return

                # 選択肢のある疑問文
                elif command[1] == "vote":
                    embed = discord.Embed(title=command[2], description="", color=discord.Colour.green())
                    select = len(command) - 3
                    if select > 10:
                        await message.channel.send("可能な選択肢は最大10個までです")
                        return

                    vote_candidate = command[3:]
                    for i in range(len(vote_candidate)):
                        embed.description += list_vote[i] + "   " + vote_candidate[i] + "\n"

                    voting_msg = await message.channel.send(embed=embed)
                    for i in range(select):
                        await voting_msg.add_reaction(list_vote[i])
                    return

                # 使い方
                elif command[1] == "help":
                    embed = discord.Embed(title="使用方法", description="", color=discord.Colour.red())
                    embed.description = (
                        emphasize("question.[TYPE].[CONTENT] + .[CANDIDATE]\n") +
                        "注意 : 質問文や選択肢に\".\"を含めないでください\n" +
                        "\n" +
                        emphasize("[TYPE] : \"yes-no\" or \"vote\"\n") +
                        underline("\"yes-no\" : \n") +
                        "Yes-No疑問文を作成します\n" +
                        "[CANDIDATE]は必要ありません\n" +
                        underline("\"vote\" : \n") +
                        "選択肢が複数ある質問を作成します\n" +
                        "[CANDIDATE]がない場合は質問文だけ表示されます\n" +
                        "\n" +
                        emphasize("[CONTENT] : \n") +
                        "質問文に相当します\n" +
                        "\n" +
                        emphasize("[CANDIDATE] : \n") +
                        "質問形式が\"vote\"である場合の選択肢です\n" +
                        "選択肢として可能な最大個数は10個までです\n"
                    )
                    await message.channel.send(embed=embed)

                # 以上のどの形式でもないものは形式不備を伝える
                else:
                    await message.channel.send("質問形式が異なっています (2つめの引数が正しくありません)")

            except IndexError:
                await message.channel.send("質問の入力形式に間違いがあります (引数が足りません)")

        # チーム分けコマンド
        elif command[0] == "team":
            try:
                team_count = int(command[1]) if len(command) > 1 else 2
                msg = self.discord_bot.make_party_num(message, team_count)
                await message.channel.send(msg)
            except ValueError:
                await message.channel.send("チーム数を整数で指定してください。")
            except Exception as e:
                print(f"Error in team command: {e}")
                await message.channel.send("エラーが発生しました。管理者に連絡してください。")

    async def on_member_join(self, member):
        try:
            await member.send("ようこそ、{}さん！サーバーに参加していただきありがとうございます。".format(member.name))
        except Exception as e:
            print(f"Failed to send welcome message: {e}")

# Discordの権限を設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()

# データベースの初期化を実行
initialize_database()

client.run(os.environ['TOKEN'])
