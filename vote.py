import discord
from helpers import list_yesno, list_vote, emphasize, underline, isContainedNoInput

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
            embed = discord.Embed(title=command[2], color=discord.Colour.green())
            if (select := len(command) - 3) > 10:
                await message.channel.send("可能な選択肢は最大10個までです")
                return
            for i, candidate in enumerate(command[3:], start=1):
                embed.description += f"{list_vote[i-1]} {candidate}\n"
            voting_msg = await message.channel.send(embed=embed)
            for emoji in list_vote[:select]:
                await voting_msg.add_reaction(emoji)

        elif command[1] == "help":
            embed = discord.Embed(title="使用方法", color=discord.Colour.red())
            embed.description = (
                emphasize("question.[TYPE].[CONTENT] + .[CANDIDATE]\n") +
                "注意 : 質問文や選択肢に\".\"を含めないでください\n" +
                emphasize("[TYPE] : \"yes-no\" or \"vote\"\n") +
                underline("\"yes-no\" : \n") +
                "Yes-No疑問文を作成します\n" +
                "[CANDIDATE]は必要ありません\n" +
                underline("\"vote\" : \n") +
                "選択肢が複数ある質問を作成します\n" +
                "[CANDIDATE]がない場合は質問文だけ表示されます\n" +
                emphasize("[CONTENT] : \n") +
                "質問文に相当します\n" +
                emphasize("[CANDIDATE] : \n") +
                "質問形式が\"vote\"である場合の選択肢です\n" +
                "選択肢として可能な最大個数は10個までです\n"
            )
            await message.channel.send(embed=embed)

        else:
            await message.channel.send("質問形式が異なっています (2つめの引数が正しくありません)")

    except IndexError:
        await message.channel.send("質問の入力形式に間違いがあります (引数が足りません)")
