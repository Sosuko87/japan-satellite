import json
import random

# Scratch公式のID生成用文字セット
SOUP = "!#%()*+,-./:;=?@[]^_`{|}~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def generate_scratch_id(length=20):
    # Scratch標準は20文字のランダム文字列
    return ''.join(random.choices(SOUP, k=length))

with open("project.json", "r", encoding="utf-8") as f:
    data = json.load(f)

id_map = {}

# 1. 既存のIDを収集して新しいIDをマッピング（重複防止のためsetで管理）
used_ids = set()

for target in data.get("targets", []):
    for category in ["variables", "lists", "broadcasts", "blocks", "comments"]:
        for old_id in target.get(category, {}).keys():
            if old_id not in id_map:
                new_id = generate_scratch_id()
                while new_id in used_ids:
                    new_id = generate_scratch_id()
                used_ids.add(new_id)
                id_map[old_id] = new_id

# 2. JSON内のすべての該当IDを一括置換
def replace_ids(obj):
    if isinstance(obj, dict):
        return {id_map.get(k, k): replace_ids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_ids(item) for item in obj]
    elif isinstance(obj, str):
        return id_map.get(obj, obj)
    return obj

new_data = replace_ids(data)

with open("project_new.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, separators=(",", ":"))
