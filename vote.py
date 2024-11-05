import discord
from helpers import list_yesno, list_vote, emphasize, underline, isContainedNoInput
from datetime import datetime, timedelta
from scheduler import scheduler

async def handle_question_navigation(command, message):
    await message.channel.send("質問形式を選択してください: `yes-no` または `vote`")

    def check(msg):
        return msg.author == message.author and msg.channel == message.channel

    try:
        # 質問形式の取得
        type_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        question_type = type_msg.content.strip().lower()

        # 質問内容の取得
        await message.channel.send("質問内容を入力してください。")
        question_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        question_content = question_msg.content

        # 期限の取得
        await message.channel.send("投票の期限を入力してください（例: 10m, 1h, 2d）。")
        duration_msg = await message.client.wait_for('message', check=check, timeout=60.0)
        duration_str = duration_msg.content

        # 期限の計算
        duration = parse_duration(duration_str)
        if not duration:
            await message.channel.send("期限の形式が正しくありません。例: 10m, 1h, 2d")
            return

        expiration_time = datetime.now() + duration

        if question_type == "yes-no":
            embed = discord.Embed(title=question_content, color=discord.Colour.blue())
            voting_msg = await message.channel.send(embed=embed)
            for emoji in list_yesno:
                await voting_msg.add_reaction(emoji)

        elif question_type == "vote":
            await message.channel.send("投票の選択肢をスペースで区切って入力してください（最大10個）。")
            options_msg = await message.client.wait_for('message', check=check, timeout=60.0)
            options = options_msg.content.split()

            if len(options) > 10:
                await message.channel.send("可能な選択肢は最大10個までです。")
                return

            embed = discord.Embed(title=question_content, color=discord.Colour.green())
            embed.description = "\n".join(f"{list_vote[i]} {opt}" for i, opt in enumerate(options))
            voting_msg = await message.channel.send(embed=embed)

            for emoji in list_vote[:len(options)]:
                await voting_msg.add_reaction(emoji)
        else:
            await message.channel.send("無効な質問形式です。")

        # 期限の設定
        scheduler.add_job(end_voting, 'date', run_date=expiration_time, args=[message.channel, voting_msg.id])

    except discord.TimeoutError:
        await message.channel.send("タイムアウトしました。再度コマンドを実行してください。")

def parse_duration(duration_str):
    units = {'m': 'minutes', 'h': 'hours', 'd': 'days'}
    if duration_str[-1] in units:
        try:
            value = int(duration_str[:-1])
            return timedelta(**{units[duration_str[-1]]: value})
        except ValueError:
            return None
    return None

async def end_voting(channel, message_id):
    try:
        msg = await channel.fetch_message(message_id)
        await channel.send(f"⏰ 投票が締め切られました: {msg.embeds[0].title}")
    except discord.NotFound:
        await channel.send("投票メッセージが見つかりませんでした。")
