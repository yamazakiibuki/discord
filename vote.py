import discord
from datetime import datetime
import asyncio
from database import save_vote, get_votes, delete_vote_entry, ensure_guild_settings

async def handle_question_navigation(command, message, client):
    if len(command) < 2:
        await message.channel.send("コマンドが不完全です。利用可能なコマンド:\n- `!question yes-no 質問内容`\n- `!question vote`\n- `!question list`\n- `!question delete 投票ID`")
        return

    question_type = command[1]

    if question_type == "yes-no":
        if len(command) < 3:
            await message.channel.send("質問内容を指定してください。例: `!question yes-no この機能は便利ですか？`")
            return
        await create_yes_no_question(command, message)
    elif question_type == "vote":
        await create_vote_question_step_by_step(message, client)
    elif question_type == "list":
        await list_votes(message)
    elif question_type == "delete":
        if len(command) < 3:
            await message.channel.send("削除する投票のIDを指定してください。例: `!question delete 1`")
            return
        await delete_vote(command, message)
    else:
        await message.channel.send("無効な質問タイプです。利用可能なコマンドは `yes-no`, `vote`, `list`, `delete` です。")

async def create_yes_no_question(command, message):
    question = command[2]
    embed = discord.Embed(title=question, color=discord.Colour.blue())
    voting_msg = await message.channel.send(embed=embed)
    await voting_msg.add_reaction('✅')
    await voting_msg.add_reaction('❌')
    await message.channel.send("✅ または ❌ で投票してください！")

async def create_vote_question_step_by_step(message, client):
    """インタラクティブに投票を作成する"""
    await message.channel.send("新しい投票を作成します。まず質問を入力してください（例: どのゲームが好きですか？）。")

    def check(m):
        return m.author == message.author and m.channel == message.channel

    try:
        # 質問の入力
        question_msg = await client.wait_for('message', check=check, timeout=60.0)
        question = question_msg.content

        # 選択肢の入力
        await message.channel.send("選択肢をカンマ区切りで入力してください（例: はい,いいえ,たぶん）。最大10個まで指定可能です。")
        options_msg = await client.wait_for('message', check=check, timeout=60.0)
        options = [opt.strip() for opt in options_msg.content.split(',')]

        if len(options) > 10:
            await message.channel.send("選択肢は最大10個までです。")
            return

        # 有効期限の設定
        await message.channel.send("投票の有効期限を入力してください（例: 2024-12-25 15:00）。スキップする場合はそのままEnterを押してください。")
        expiration_msg = await client.wait_for('message', check=check, timeout=60.0)
        expiration = expiration_msg.content

        if expiration:
            try:
                expiration = datetime.strptime(expiration, '%Y-%m-%d %H:%M')
            except ValueError:
                await message.channel.send("日付と時刻の形式が正しくありません。例: 2024-12-25 15:00")
                return
        else:
            expiration = None

        # 必要な設定データの確認・挿入
        ensure_guild_settings(message.guild.id)

        # 投票を保存
        save_vote(message.guild.id, question, options, expiration)

        # 投票の表示
        embed = discord.Embed(title=question, color=discord.Colour.green())
        for i, option in enumerate(options):
            embed.description = (embed.description or '') + f"{i + 1}. {option}\n"
        voting_msg = await message.channel.send(embed=embed)

        for i in range(len(options)):
            await voting_msg.add_reaction(f"{i + 1}\N{COMBINING ENCLOSING KEYCAP}")

        await message.channel.send("投票が作成されました！リアクションを使って投票してください！")

    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください。")

async def list_votes(message):
    votes = get_votes(message.guild.id)
    if not votes:
        await message.channel.send("現在の投票はありません。")
        return

    embed = discord.Embed(title="投票一覧", color=discord.Colour.gold())
    for vote in votes:
        expiration_date = datetime.strptime(vote['expiration'], '%Y-%m-%d %H:%M') if vote['expiration'] else "なし"
        result = vote['results'] if vote['results'] else '未定'
        embed.add_field(name=vote['question'], value=f"結果: {result}\n有効期限: {expiration_date}", inline=False)
    await message.channel.send(embed=embed)

async def delete_vote(command, message):
    vote_id = int(command[2])
    success = delete_vote_entry(vote_id)
    if success:
        await message.channel.send(f"投票 ID {vote_id} を削除しました。")
    else:
        await message.channel.send("指定された投票は見つかりません。")
