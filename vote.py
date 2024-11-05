import discord
from datetime import datetime
from database import save_vote, get_votes, delete_vote

async def handle_question_navigation(command, message):
    await message.channel.send("投票の質問内容を入力してください。")

    def check(msg):
        return msg.author == message.author and msg.channel == message.channel

    try:
        question_msg = await message.channel.send("質問を入力してください。")
        question = await message.channel.client.wait_for('message', check=check, timeout=60.0)

        await message.channel.send("選択肢を入力してください（例: 肢1).(選択肢2)...）")
        options_msg = await message.channel.client.wait_for('message', check=check, timeout=60.0)
        options = options_msg.content.split('.')

        await message.channel.send("投票の期限を入力してください（例: 2024-12-25 15:00）。")
        deadline_msg = await message.channel.client.wait_for('message', check=check, timeout=60.0)
        deadline_str = deadline_msg.content

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")

        if deadline < datetime.now():
            await message.channel.send("指定された日時は過去です。未来の日時を指定してください。")
            return

        await save_vote(message.guild.id, question.content, options, deadline.isoformat())
        await message.channel.send("投票が作成されました！")

    except discord.TimeoutError:
        await message.channel.send("タイムアウトしました。再度コマンドを実行してください。")

async def show_votes(message):
    votes = get_votes(message.guild.id)
    if not votes:
        await message.channel.send("現在、登録されている投票はありません。")
        return

    for vote in votes:
        vote_id, guild_id, question, options, deadline, results = vote
        options_list = json.loads(options)
        results_dict = json.loads(results)
        results_display = {option: results_dict.get(option, "未定") for option in options_list}
        await message.channel.send(f"投票 ID: {vote_id}\n質問: {question}\n選択肢: {options_list}\n結果: {results_display}\n期限: {deadline}")

async def delete_vote_command(vote_id, message):
    delete_vote(vote_id)
    await message.channel.send(f"投票 ID {vote_id} が削除されました。")
