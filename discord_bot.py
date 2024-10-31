from utils import random, emphasize

class DiscordBot:
    def __init__(self):
        self.channel_mem = []
        self.mem_len = 0
        self.vc_state_err = '実行できません。ボイスチャンネルに入ってコマンドを実行してください。'

    def set_mem(self, ctx):
        state = ctx.author.voice
        if state is None:
            return False
        self.channel_mem = [i.name for i in state.channel.members]
        self.mem_len = len(self.channel_mem)
        return True

    # チーム数を指定した場合のチーム分け
    def make_party_num(self, ctx, party_num):
        team = []
        remainder = []

        if self.set_mem(ctx) is False:
            return self.vc_state_err

        if party_num > self.mem_len or party_num <= 0:
            return '実行できません。チーム分けできる数を指定してください。'

        random.shuffle(self.channel_mem)
        for i in range(party_num):
            team.append(f"=====チーム {i + 1}=====")
            team.extend(self.channel_mem[i::party_num])

        return '\n'.join(team)
