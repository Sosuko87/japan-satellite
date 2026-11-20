import os
import zipfile
import scratchattach as sa

# --- 設定情報 ---
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login('Kahu-tositai', PASSWORD)
project = session.connect_project("1442732643")

# 1. .sb3（実体はZIPファイル）から画像・音声を直接取り出して送信する
with zipfile.ZipFile("3DSplatoon.sb3", "r") as z:
    for filename in z.namelist():
        if filename == "project.json" or filename.endswith("/"):
            continue
        asset_id, file_ext = filename.rsplit(".", 1)
        session.upload_asset(
            z.read(filename),
            asset_id=asset_id,
            file_ext=file_ext.lower()
        )

# 2. アセットを送り終えてからプロジェクト本体を保存する
pb = sa.read_sb3_file("3DSplatoon.sb3")
project.set_body(pb)
