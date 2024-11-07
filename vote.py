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
        await create_vote_question_step_by_step(message)
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

async def create_vote_question_step_by_step(message):
    """ガイド付きで投票を作成する"""
    await message.channel.send("新しい投票を作成します。質問を入力してください。")

    def check(m):
        return m.author == message.author and m.channel == message.channel

    try:
        question_msg = await message.channel.send("質問を入力してください。")
        question_response = await message.channel.send("質問: ")
        question = question_response.content

        await message.channel.send("選択肢 .
