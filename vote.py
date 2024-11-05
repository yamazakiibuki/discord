import discord
from helpers import list_yesno, list_vote, emphasize, underline, isContainedNoInput
import asyncio

async def handle_question(message):
    def check(m):
        return m.author == message.author and m.channel == message.channel

    # ステップ1: 質問のタイプを尋ねる
    await message.channel.send("質問のタイプを選んでください。`yes-no` または `vote` のいずれかを入力してください。")
    try:
        question_type_msg = await client.wait_for('message', timeout=60.0, check=check)
        question_type = question_type_msg.content.strip().lower()

        if question_type not in ["yes-no", "vote"]:
            await message.channel.send("無効なタイプです。`yes-no` または `vote` のいずれかを入力してください。")
            return

    except asyncio.TimeoutError:
        await message.channel.send("時間が切れました。再度コマンドを入力してください。")
        return

    # ステップ2: 質問の内容を尋ねる
    await message.channel.send("質問の内容を入力してください。")
    try:
        content_msg = await client.wait_for('message', timeout=60.0, check=check)
        content = content_msg.content.strip()

    except asyncio.TimeoutError:
        await message.channel.send("時間が切れました。再度コマンドを入力してください。")
        return

    if question_type == "yes-no":
        embed = discord.Embed(title=content, color=discord.Colour.blue())
        voting_msg = await message.channel.send(embed=embed)
        for emoji in list_yesno:
            await voting_msg.add_reaction(emoji)

    elif question_type == "vote":
        await message.channel.send("選択肢を最大10個まで入力してください。選択肢の入力が終わったら、`完了` と入力してください。")
        candidates = []

        while True:
            try:
                candidate_msg = await client.wait_for('message', timeout=60.0, check=check)
                candidate = candidate_msg.content.strip()

                if candidate.lower() == "完了":
                    break
                if len(candidates) >= 10:
                    await message.channel.send("選択肢は最大10個までです。これ以上は追加できません。")
                    continue

                candidates.append(candidate)

            except asyncio.TimeoutError:
                await message.channel.send("時間が切れました。再度コマンドを入力してください。")
                return

        embed = discord.Embed(title=content, color=discord.Colour.green())
        embed.description = "\n".join([f"{list_vote[i]} {candidate}" for i, candidate in enumerate(candidates, start=1)])
        voting_msg = await message.channel.send(embed=embed)
        for emoji in list_vote[:len(candidates)]:
            await voting_msg.add_reaction(emoji)

    else:
        await message.channel.send("質問形式が異なっています。")

