import discord
import asyncio  # asyncioをインポート
from helpers import list_yesno, list_vote, emphasize, underline, isContainedNoInput

async def handle_question_navigation(command, message, client):
    def check(msg):
        return msg.author == message.author and msg.channel == message.channel

    try:
        await message.channel.send("質問形式を選択してください: `yes-no` または `vote`")
        type_msg = await client.wait_for('message', check=check, timeout=60.0)
        question_type = type_msg.content.lower()

        await message.channel.send("質問内容を入力してください。")
        content_msg = await client.wait_for('message', check=check, timeout=60.0)
        content = content_msg.content

        await message.channel.send("投票の期限を入力してください（例: 10m, 1h, 2d）。")
        duration_msg = await client.wait_for('message', check=check, timeout=60.0)
        duration = duration_msg.content

        if question_type == "yes-no":
            embed = discord.Embed(title=content, color=discord.Colour.blue())
            voting_msg = await message.channel.send(embed=embed)
            for emoji in list_yesno:
                await voting_msg.add_reaction(emoji)

        elif question_type == "vote":
            await message.channel.send("投票の選択肢をスペースで区切って入力してください（最大10個）。")
            options_msg = await client.wait_for('message', check=check, timeout=60.0)
            options = options_msg.content.split()[:10]

            embed = discord.Embed(title=content, color=discord.Colour.green())
            embed.description = "\n".join(f"{list_vote[i]} {option}" for i, option in enumerate(options))
            voting_msg = await message.channel.send(embed=embed)
            for i in range(len(options)):
                await voting_msg.add_reaction(list_vote[i])

        # 期限が切れたら投票を締め切る処理
        await asyncio.sleep(parse_duration(duration))
        await message.channel.send("⏰ 投票が締め切られました！")

    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。もう一度やり直してください。")

def parse_duration(duration_str):
    """ '10m', '1h', '2d' のような形式の時間を秒に変換 """
    unit = duration_str[-1]
    amount = int(duration_str[:-1])
    if unit == 'm':
        return amount * 60
    elif unit == 'h':
        return amount * 3600
    elif unit == 'd':
        return amount * 86400
    else:
        raise ValueError("Invalid duration format.")
