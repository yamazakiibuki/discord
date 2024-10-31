from database import save_settings, load_settings
import discord

async def set_channel(command, message):
    if len(command) < 3:
        await message.channel.send("チャンネル名を指定してください。使用法: `set_channel.[BOT_ROOM|ANNOUNCE_CHANNEL].[CHANNEL_NAME]`")
        return

    channel_type, channel_name = command[1], command[2]
    channel = discord.utils.get(message.guild.channels, name=channel_name)

    if not channel:
        await message.channel.send("指定されたチャンネル名が見つかりません。")
        return

    guild_id = message.guild.id
    if channel_type == "BOT_ROOM":
        save_settings(guild_id, channel.id, load_settings(guild_id)[1])
        await message.channel.send(f"ボットルームを `{channel.name}` に設定しました。")
    elif channel_type == "ANNOUNCE_CHANNEL":
        _, announce_channel_ids = load_settings(guild_id)
        announce_channel_ids.append(channel.id)
        save_settings(guild_id, load_settings(guild_id)[0], announce_channel_ids)
        await message.channel.send(f"アナウンスチャンネルを `{channel.name}` に設定しました。")
    else:
        await message.channel.send("チャンネルタイプが無効です。`BOT_ROOM` または `ANNOUNCE_CHANNEL` を指定してください。")
