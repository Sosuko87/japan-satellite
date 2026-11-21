import json
import zipfile

def load_project_json(sb3_path):
    with zipfile.ZipFile(sb3_path, "r") as z:
        return json.loads(z.read("project.json").decode("utf-8"))

before = load_project_json("3DSplatoon.sb3")
after = load_project_json("after.sb3")

# 1. TurboWarp隠し設定 (_twconfig_) の比較
def get_twconfig(data):
    for t in data["targets"]:
        for c in t.get("comments", {}).values():
            if "_twconfig_" in c.get("text", ""):
                return c["text"]
    return "なし"

print("--- 1. TurboWarp隠し設定 ---")
print("アップロード前:", get_twconfig(before))
print("アップロード後:", get_twconfig(after))

# 2. 定義ブロックの「画面を再描画せずに実行 (warp)」の数を確認
def count_warp_blocks(data):
    count = 0
    for t in data["targets"]:
        for b in t.get("blocks", {}).values():
            if isinstance(b, dict) and b.get("opcode") == "procedures_prototype":
                if str(b.get("mutation", {}).get("warp")).lower() == "true":
                    count += 1
    return count

print("\n--- 2. 高速実行（画面を再描画せずに実行）ブロック数 ---")
print("アップロード前:", count_warp_blocks(before), "個")
print("アップロード後:", count_warp_blocks(after), "個")

# 3. 拡張機能リストの比較
print("\n--- 3. 拡張機能情報 ---")
print("アップロード前 extensions:", before.get("extensions"))
print("アップロード後 extensions:", after.get("extensions"))
print("アップロード前 extensionURLs:", before.get("extensionURLs"))
print("アップロード後 extensionURLs:", after.get("extensionURLs"))
