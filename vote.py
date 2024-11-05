import discord
from helpers import list_yesno, list_vote, emphasize, underline, isContainedNoInput
import sqlite3
from datetime import datetime

async def handle_question(command, message):
    if isContainedNoInput(command):
        await message.channel.send("無効なコマンドです (セパレータが連続もしくは最後に入力されています)")
        return

    try:
        if command[1] == "yes-no":
            embed = discord.Embed(title=command[2], color=discord.Colour.blue())
            voting_msg = await message.channel.send(embed=embed)
            for emoji in list_yesno:
                await voting_msg.add_reaction(emoji)

        elif command[1] == "vote":
            await handle_question_navigation(command, message)

        elif command[1] == "list":
            await list_votes(message)

        elif command[1] == "delete":
            await delete_vote(command, message)

        elif command[1] == "help":
            await display_help(message)

        else:
            await message.channel.send("質問形式が異なっています (2つめの引数が正しくありません)")

    except IndexError:
        await message.channel.send("質問の入力形式に間違いがあります (引数が足りません)")

async def handle_question_navigation(command, message):
    await message.channel.send("投票の質問内容を入力してください。")
    
    def check(msg):
        return msg.author == message.author and msg.channel == message.channel

    try:
        question_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        question = question_msg.content

        await message.channel.send("選択肢を入力してください（例: 肢1).(選択肢2)...）")
        options_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        options = options_msg.content.split('.')

        await message.channel.send("投票の期限を入力してください（例: 2024-12-25 15:00）。")
        deadline_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        deadline_str = deadline_msg.content

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")

        if deadline < datetime.now():
            await message.channel.send("指定された日時は過去です。未来の日時を指定してください。")
            return

        await save_vote(question, options, deadline)
        await message.channel.send("投票が作成されました！")

    except discord.TimeoutError:
        await message.channel.send("タイムアウトしました。再度コマンドを実行してください。")

async def save_vote(question, options, deadline):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('INSERT INTO votes (question, options, deadline, results) VALUES (?, ?, ?, ?)',
              (question, json.dumps(options), deadline.isoformat(), json.dumps({})))
    conn.commit()
    conn.close()

async def list_votes(message):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT id, question, options, deadline FROM votes')
    votes = c.fetchall()
    conn.close()

    if not votes:
        await message.channel.send("現在の投票はありません。")
        return

    embed = discord.Embed(title="現在の投票一覧", color=discord.Colour.green())
    for vote in votes:
        vote_id, question, options, deadline = vote
        results = "未定" if datetime.fromisoformat(deadline) > datetime.now() else "投票終了"
        embed.add_field(name=f"ID: {vote_id} - {question}", value=f"選択肢: {json.loads(options)}\n期限: {deadline}\n結果: {results}", inline=False)

    await message.channel.send(embed=embed)

async def delete_vote(command, message):
    if len(command) < 3:
        await message.channel.send("削除する投票のIDを指定してください。")
        return

    vote_id = command[2]
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE id = ?', (vote_id,))
    conn.commit()
    conn.close()

    await message.channel.send(f"投票ID {vote_id} が削除されました。")

async def display_help(message):
    embed = discord.Embed(title="使用方法", color=discord.Colour.red())
    embed.description = (
        emphasize("質問コマンドの形式: !question.[TYPE].[CONTENT]\n") +
        "注意: 質問文や選択肢に\".\"を含めないでください。\n" +
        emphasize("[TYPE] : \"yes-no\" or \"vote\"\n") +
        "投票の詳細については、ボットがナビゲートします。\n"
    )
    await message.channel.send(embed=embed)
