import json
import random
from pathlib import Path

SOUP = "!#%()*+,-./:;=?@[]^_`{|}~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


class ScratchIDGenerator:
    def __init__(self, existing_ids: set[str] | None = None):
        # 元のIDとも新しいIDとも重複しないように管理
        self.used_ids = set(existing_ids) if existing_ids else set()

    def generate(self, length: int = 20) -> str:
        while True:
            new_id = "".join(random.choices(SOUP, k=length))
            if new_id not in self.used_ids:
                self.used_ids.add(new_id)
                return new_id


def replace_input_value(item, id_map: dict[str, str]):
    """
    blocks内のinputs配列を再帰的に走査し、ID参照のみを置換する。
    リテラル値（数値・文字列など: 先頭要素が4〜10の配列）は誤置換を防ぐためそのまま残す。
    """
    if isinstance(item, str):
        return id_map.get(item, item)

    if isinstance(item, list) and len(item) > 0:
        tag = item[0]
        # [4〜10, "値"] は数値やテキストのリテラルなので置換しない
        if isinstance(tag, int) and 4 <= tag <= 10:
            return item
        # [11, "メッセージ名", "broadcast_id"], [12, "変数名", "var_id"], [13, "リスト名", "list_id"]
        if isinstance(tag, int) and tag in (11, 12, 13) and len(item) >= 3:
            return [tag, item[1], id_map.get(item[2], item[2])] + item[3:]
        # それ以外（[1, "block_id"], [2, "block_id"], [3, "block_id", shadow] など）
        return [replace_input_value(elem, id_map) for elem in item]

    return item


def regenerate_project_ids(project_data: dict) -> dict:
    # 1. 全ターゲット（ステージ・スプライト）から既存の全IDを収集
    old_ids: set[str] = set()
    for target in project_data.get("targets", []):
        for category in ("variables", "lists", "broadcasts", "blocks"):
            old_ids.update(target.get(category, {}).keys())

    # 2. 旧ID -> 新ID（20文字）の対応表を作成
    id_gen = ScratchIDGenerator(existing_ids=old_ids)
    id_map: dict[str, str] = {old_id: id_gen.generate(20) for old_id in old_ids}

    # 3. 各ターゲット内の定義キーとブロック内参照を置換
    for target in project_data.get("targets", []):
        # variables / lists / broadcasts のキー置換
        for category in ("variables", "lists", "broadcasts"):
            if category in target:
                target[category] = {
                    id_map.get(k, k): v for k, v in target[category].items()
                }

        # blocks のキーおよび内部参照の置換
        if "blocks" in target:
            new_blocks = {}
            for block_id, block_data in target["blocks"].items():
                new_block_id = id_map.get(block_id, block_id)

                # トップレベルに置かれた変数・リストのレポーターブロック（配列形式）の場合
                if isinstance(block_data, list):
                    new_blocks[new_block_id] = replace_input_value(block_data, id_map)
                    continue

                # 通常のブロック（辞書形式）
                if block_data.get("next") is not None:
                    block_data["next"] = id_map.get(block_data["next"], block_data["next"])

                if block_data.get("parent") is not None:
                    block_data["parent"] = id_map.get(block_data["parent"], block_data["parent"])

                # inputs 内のブロックID・変数ID・リストID・ブロードキャストIDを置換
                if "inputs" in block_data:
                    block_data["inputs"] = {
                        input_name: replace_input_value(input_val, id_map)
                        for input_name, input_val in block_data["inputs"].items()
                    }

                # fields 内の ["名前", "ID"] の第2要素（ID）を置換
                if "fields" in block_data:
                    for field_name, field_val in block_data["fields"].items():
                        if isinstance(field_val, list) and len(field_val) >= 2 and isinstance(field_val[1], str):
                            field_val[1] = id_map.get(field_val[1], field_val[1])

                new_blocks[new_block_id] = block_data

            target["blocks"] = new_blocks

        # comments がブロックに紐づいている場合の blockId を更新
        for comment in target.get("comments", {}).values():
            if isinstance(comment, dict) and comment.get("blockId") is not None:
                comment["blockId"] = id_map.get(comment["blockId"], comment["blockId"])

    # 4. ステージ上のモニター表示（変数・リスト表示枠）のIDを更新
    for monitor in project_data.get("monitors", []):
        if isinstance(monitor, dict) and "id" in monitor:
            monitor["id"] = id_map.get(monitor["id"], monitor["id"])

    return project_data


# --- 実行例 ---
if __name__ == "__main__":
    input_path = Path("project.json")
    output_path = Path("project_new_ids.json")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    updated_data = regenerate_project_ids(data)

    with output_path.open("w", encoding="utf-8") as f:
        # Scratchのproject.jsonはコンパクト出力（separators指定）にすると容量を抑えられる
        json.dump(updated_data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"変換完了: {output_path}")
