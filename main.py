import json, random, re

soup = "!#%()*+,-./:;=?@[]^_`{|}~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
with open("project.json", "r", encoding="utf-8") as f:
    text = f.read()

# v_数字 のIDをすべて抽出して20文字のランダムIDに一括置換
old_ids = set(re.findall(r'"(v_\d+)"', text))
for old_id in sorted(old_ids, key=len, reverse=True):
    new_id = "".join(random.choice(soup) for _ in range(20))
    text = text.replace(f'"{old_id}"', f'"{new_id}"')

with open("project_fixed.json", "w", encoding="utf-8") as f:
    f.write(text)
