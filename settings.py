import discord

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
        "まず、`BOT_ROOM` に設定するチャンネル名を入力してください。\n"
        "例: `general`"
    )

async def handle_channel_setup(message, temporary_settings):
    user_id = message.author.id

    if user_id not in temporary_settings:
        await message.channel.send("最初に `!set_channel` を実行してください。")
        return

    settings = temporary_settings[user_id]
    step = settings["step"]

    if step == 1:
        # BOT_ROOMの設定
        channel_name = message.content.strip()
        guild_id = settings["guild_id"]
        channel = discord.utils.get(message.guild.channels, name=channel_name)

        if not channel:
            await message.channel.send(
                f"指定されたチャンネル名 `{channel_name}` が見つかりません。\n"
                "正しいチャンネル名を入力してください。"
            )
            return

        # BOT_ROOMを保存し、次のステップへ進む
        settings["bot_room_id"] = channel.id
        settings["step"] = 2
        await message.channel.send(
            f"`BOT_ROOM` に `{channel_name}` を設定しました。\n"
            "次に、`ANNOUNCE_CHANNEL` に設定するチャンネル名を入力してください。\n"
            "例: `announcements`"
        )
    elif step == 2:
        # ANNOUNCE_CHANNELの設定
        channel_name = message.content.strip()
        guild_id = settings["guild_id"]
        channel = discord.utils.get(message.guild.channels, name=channel_name)

        if not channel:
            await message.channel.send(
                f"指定されたチャンネル名 `{channel_name}` が見つかりません。\n"
                "正しいチャンネル名を入力してください。"
            )
            return

        try:
            # 設定を保存
            bot_room_id = settings["bot_room_id"]
            save_settings(guild_id, bot_room_id, [channel.id])

            # 設定完了
            del temporary_settings[user_id]  # 一時データを削除
            await message.channel.send(
                f"`ANNOUNCE_CHANNEL` に `{channel_name}` を設定しました！\n"
                "設定が完了しました。"
            )
        except Exception as e:
            await message.channel.send("設定を保存中にエラーが発生しました。詳細は管理者に問い合わせてください。")
            print(f"DEBUG: 設定保存エラー - {e}")
