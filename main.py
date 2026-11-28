import json
import random

SOUP = "!#%()*+,-./:;=?@[]^_`{|}~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def generate_scratch_id(length=20):
    return ''.join(random.choices(SOUP, k=length))

with open("project.json", "r", encoding="utf-8") as f:
    data = json.load(f)

id_map = {}
used_ids = set()

def get_new_id(old_id):
    if not old_id or not isinstance(old_id, str):
        return old_id
    if old_id not in id_map:
        new_id = generate_scratch_id()
        while new_id in used_ids:
            new_id = generate_scratch_id()
        used_ids.add(new_id)
        id_map[old_id] = new_id
    return id_map[old_id]

# 1. まずターゲット内の定義（キー）を置換してマップを作成
for target in data.get("targets", []):
    for category in ["variables", "lists", "broadcasts", "blocks", "comments"]:
        if category in target:
            new_cat = {}
            for old_id, val in target[category].items():
                new_cat[get_new_id(old_id)] = val
            target[category] = new_cat

# 2. 参照箇所（特定のキー・配列位置）だけをピンポイントで置換
for target in data.get("targets", []):
    # ブロック内の参照
    for block_id, block in target.get("blocks", {}).items():
        if not isinstance(block, dict):
            continue
        # parent, next, comment のIDを置換
        for ref_key in ["parent", "next", "comment"]:
            if block.get(ref_key) in id_map:
                block[ref_key] = id_map[block[ref_key]]
        
        # inputs内のブロックID・変数ID・リストIDを置換
        for inp_name, inp_val in block.get("inputs", {}).items():
            if isinstance(inp_val, list):
                for i in range(1, len(inp_val)):
                    item = inp_val[i]
                    if isinstance(item, str) and item in id_map:
                        inp_val[i] = id_map[item]
                    # 変数・リスト参照の配列 [12, "変数名", "変数ID"] や [13, "リスト名", "リストID"]
                    elif isinstance(item, list) and len(item) >= 3 and item[0] in:
                        if item[2] in id_map:
                            item[2] = id_map[item[2]]

        # fields内の変数ID・リストID・メッセージIDを置換 ([ "名前", "ID" ] の形式)
        for field_name, field_val in block.get("fields", {}).items():
            if isinstance(field_val, list) and len(field_val) >= 2:
                if field_val[1] in id_map:
                    field_val[1] = id_map[field_val[1]]

    # コメント内の blockId 参照
    for comment_id, comment in target.get("comments", {}).items():
        if isinstance(comment, dict) and comment.get("blockId") in id_map:
            comment["blockId"] = id_map[comment["blockId"]]

# 3. ステージモニター（画面上の変数・リスト表示）のIDを置換
for monitor in data.get("monitors", []):
    if monitor.get("id") in id_map:
        monitor["id"] = id_map[monitor["id"]]

with open("project_new.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
