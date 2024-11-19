from database import save_settings, load_settings
import discord

# グローバル辞書で一時的な設定情報を保持
temporary_settings = {}

async def set_channel(message, temporary_settings):
    user_id = message.author.id
    guild_id = message.guild.id

    if user_id in temporary_settings:
        await message.channel.send("現在進行中の設定があります。終了するにはもう一度コマンドを入力してください。")
        return

    # 一時的にユーザー情報を保存
    temporary_settings[user_id] = {"guild_id": guild_id, "step": 1}
    await message.channel.send(
        "設定を始めます。\n"
        "最初にチャンネルタイプを選択してください。\n"
        "`BOT_ROOM` または `ANNOUNCE_CHANNEL` を指定します。\n"
        "例: `BOT_ROOM`"
    )

async def handle_channel_setup(message, temporary_settings):
    user_id = message.author.id

    if user_id not in temporary_settings:
        await message.channel.send("最初に `!set_channel` を実行してください。")
        return

    settings = temporary_settings[user_id]
    step = settings["step"]

    if step == 1:
        channel_type = message.content.strip()
        if channel_type not in ["BOT_ROOM", "ANNOUNCE_CHANNEL"]:
            await message.channel.send("無効なチャンネルタイプです。`BOT_ROOM` または `ANNOUNCE_CHANNEL` を入力してください。")
            return

        # チャンネルタイプを保存し、次のステップへ
        settings["channel_type"] = channel_type
        settings["step"] = 2
        await message.channel.send(
            f"{channel_type} に設定するチャンネル名を入力してください。\n"
            "例: `general`"
        )
    elif step == 2:
        channel_name = message.content.strip()
        guild_id = settings["guild_id"]
        channel_type = settings["channel_type"]
        channel = discord.utils.get(message.guild.channels, name=channel_name)

        if not channel:
            await message.channel.send(
                f"指定されたチャンネル名 `{channel_name}` が見つかりません。\n"
                "正しいチャンネル名を入力してください。"
            )
            return

        # データベースに保存
        try:
            save_settings(guild_id, channel_type, channel.id)
        except Exception as e:
            await message.channel.send(f"エラーが発生しました: {e}")
            return

        # 一時的な設定を削除
        del temporary_settings[user_id]

        await message.channel.send(
            f"{channel_name} チャンネルを {channel_type} に設定しました！"
        )
