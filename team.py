import random
import discord

async def split_into_teams(voice_channel: discord.VoiceChannel, team_count: int):
    # チャンネル内のメンバーを取得
    members = [member.name for member in voice_channel.members]
    member_count = len(members)

    # メンバーがチーム数より少ない場合のチェック
    if team_count <= 0 or team_count > member_count:
        return None, "チーム数が不適切です。メンバー数以下のチーム数を指定してください。"

    # メンバーをランダムにシャッフル
    random.shuffle(members)

    # チーム分けを実行
    teams = [[] for _ in range(team_count)]
    for i, member in enumerate(members):
        teams[i % team_count].append(member)

    # 結果を整形
    response = "チーム分け結果:\n"
    for i, team in enumerate(teams, start=1):
        response += f"\n**チーム {i}**\n" + "\n".join(team)

    return teams, response
