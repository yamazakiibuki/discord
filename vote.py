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
        await create_vote_question(command, message)
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

async def create_vote_question(command, message):
    if len(command) < 4:
        await message.channel.send("投票の選択肢を指定してください。")
        return

    question = command[2]
    options = command[3:-1]
    expiration = command[-1] if len(command) > 4 else None

    # expirationのフォーマット確認
    if expiration:
        try:
            datetime.strptime(expiration, '%Y-%m-%d %H:%M')
        except ValueError:
            await message.channel.send("期限の形式が正しくありません。例: 2024-12-25 15:00")
            return

    # 選択肢の制限をチェック
    if len(options) > 10:
        await message.channel.send("選択肢は最大10個までです。")
        return

    save_vote(question, options, expiration)

    embed = discord.Embed(title=question, color=discord.Colour.green())
    for i, option in enumerate(options):
        embed.description += f"{i + 1}. {option}\n"
    voting_msg = await message.channel.send(embed=embed)

    for i in range(len(options)):
        await voting_msg.add_reaction(str(i + 1) + '️⃣')

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
