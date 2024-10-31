import random

# 投票用のリアクション絵文字
list_yesno = ['🙆‍♂️', '🙅‍♂️']
list_vote = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

# 強調フォーマット
def emphasize(text):
    return "**" + text + "**"

def underline(text):
    return "__" + text + "__"

# 入力が空かチェックする関数
def isContainedNoInput(command):
    return any(i == '' for i in command)
