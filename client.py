import discord
from database import save_settings, load_settings
from discord_bot import DiscordBot
from utils import list_yesno, list_vote, emphasize, underline

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.discord_bot = DiscordBot()

    async def on_ready(self):
        print('Startup Success!!!')

    async def on_message(self, message):
        if message.author.bot:
            return

        command = message.content.split(".")
        if command[0] == "set_channel":
            await self.handle_set_channel(message, command)
        elif command[0] == "question":
            await self.handle_question(message, command)
        elif command[0] == "team":
            await self.handle_team(message, command)

    async def handle_set_channel(self, message, command):
        if len(command) < 3:
            await message.channel.send("チャンネル名を指定してください。")
            return

        channel_type = command[1]
        channel_name = command[2]
        guild_id = message.guild.id
        channel = discord.utils.get(message.guild.channels, name=channel_name)
        
        if not channel:
            await message.channel.send("指定されたチャンネル名が見つかりません。")
            return

        if channel_type == "BOT_ROOM":
            save_settings(guild_id, channel.id, load_settings(guild_id)[1])
            await message.channel.send(f"ボットルームを `{channel.name}` に設定しました。")
        elif channel_type == "ANNOUNCE_CHANNEL":
            _, announce_channel_ids = load_settings(guild_id)
            announce_channel_ids.append(channel.id)
            save_settings(guild_id, load_settings(guild_id)[0], announce_channel_ids)
            await message.channel.send(f"アナウンスチャンネルを `{channel.name}` に設定しました。")

    async def handle_question(self, message, command):
        if len(command) < 2:
            await message.channel.send("質問の形式に誤りがあります。")
            return

        if command[1] == "yes-no":
            embed = discord.Embed(title=command[2], color=discord.Colour.blue())
            voting_msg = await message.channel.send(embed=embed)
            for emoji in list_yesno:
                await voting_msg.add_reaction(emoji)

        elif command[1] == "vote":
            embed = discord.Embed(title=command[2], color=discord.Colour.green())
            for i, candidate in enumerate(command[3:]):
                embed.description += f"{list_vote[i]} {candidate}\n"
            voting_msg = await message.channel.send(embed=embed)
            for i in range(len(command) - 3):
                await voting_msg.add_reaction(list_vote[i])

    async def handle_team(self, message, command):
        team_count = int(command[1]) if len(command) > 1 else 2
        msg = self.discord_bot.make_party_num(message, team_count)
        await message.channel.send(msg)

    async def on_member_join(self, member):
        await member.send(f"ようこそ、{member.name}さん！サーバーに参加していただきありがとうございます。")
