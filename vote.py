import discord
from datetime import datetime
from database import save_vote, get_votes, delete_vote_entry

async def handle_question_navigation(command, message, client):
    if len(command) < 3:
        await message.channel.send("コマンドが不完全です。")
        return

    question_type = command[1]

    if question_type == "yes-no":
        await create_yes_no_question(command, message)
    elif question_type == "vote":
        await create_vote_question_step_by_step(message, client)
    elif question_type == "list":
        await list_votes(message)
    elif question_type == "delete":
        await delete_vote(command, message)
    else:
        await message.channel.send("無効な質問タイプです。")

async def create_yes_no_question(command, message):
    embed = discord.Embed(title=command[2], color=discord.Colour.blue())
    voting_msg = await message.channel.send(embed=embed)
    await voting_msg.add_reaction('✅')
    await voting_msg.add_reaction('❌')

async def create_vote_question_step_by_step(message, client):
    """ガイド付きで投票を作成する"""
    await message.channel.send("新しい投票を作成します。質問を入力してください。")

    def check(m):
        return m.author == message.author and m.channel == message.channel

    try:
        question_msg = await message.channel.send("質問を入力してください。")
        question_response = await client.wait_for('message', check=check, timeout=60.0)
        question = question_response.content

        await message.channel.send("選択肢をカンマで区切って入力してください（例: はい,いいえ,たぶん）。最大10個まで指定できます。")
        options_msg = await client.wait_for('message', check=check, timeout=60.0)
        options = [opt.strip() for opt in options_msg.content.split(',')]

        if len(options) > 10:
            await message.channel.send("選択肢は最大10個までです。")
            return

        # ステップ 3: 有効期限の入力（任意）
        await message.channel.send("投票の有効期限を指定してください（例: 2024-12-25 15:00）。スキップする場合は「スキップ」と入力してください。")
        expiration_msg = await client.wait_for('message', check=check, timeout=60.0)
        expiration = expiration_msg.content

        if expiration.lower() != "スキップ":
            try:
                expiration = datetime.strptime(expiration, '%Y-%m-%d %H:%M')
            except ValueError:
                await message.channel.send("日付と時刻の形式が正しくありません。例: 2024-12-25 15:00")
                return
        else:
            expiration = None

        # 投票の保存
        save_vote(question, options, expiration.strftime('%Y-%m-%d %H:%M') if expiration else None)

        # 投票を表示
        embed = discord.Embed(title=question, color=discord.Colour.green())
        for i, option in enumerate(options):
            embed.description = (embed.description or '') + f"{i + 1}. {option}\n"
        voting_msg = await message.channel.send(embed=embed)

        # リアクションを追加
        for i in range(len(options)):
            await voting_msg.add_reaction(str(i + 1) + '️⃣')

        await message.channel.send("投票が作成されました。リアクションを使って投票を行ってください！")

    except discord.TimeoutError:
        await message.channel.send("タイムアウトしました。もう一度最初からやり直してください。")

async def list_votes(message):
    votes = get_votes()
    if not votes:
        await message.channel.send("現在の投票はありません。")
        return

    embed = discord.Embed(title="投票一覧", color=discord.Colour.gold())
    for vote in votes:
        expiration_date = datetime.strptime(vote['expiration'], '%Y-%m-%d %H:%M')
        result = vote['results'] if datetime.now() < expiration_date else '未定'
        embed.add_field(name=vote['question'], value=f"結果: {result or '未定'}", inline=False)
    await message.channel.send(embed=embed)

async def delete_vote(command, message):
    if len(command) < 3:
        await message.channel.send("削除する投票のIDを指定してください。")
        return

    vote_id = int(command[2])
    success = delete_vote_entry(vote_id)
    if success:
        await message.channel.send(f"投票 ID {vote_id} を削除しました。")
    else:
        await message.channel.send("指定された投票は見つかりません。")
