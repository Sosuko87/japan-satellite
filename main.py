import os
import scratchattach as sa

# --- 設定情報 ---
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login('Kahu-tositai', PASSWORD)
project = session.connect_project("1442732643")

pb = sa.read_sb3_file("3DSplatoon.sb3")

# 1. pb.assets() のように () を付けて画像・音声データを取得・送信する
for filename, data in pb.assets().items():
    asset_id, file_ext = filename.rsplit(".", 1)
    session.upload_asset(data, asset_id=asset_id, file_ext=file_ext)

# 2. アセットを送り終えてからプロジェクト本体を保存する
project.set_body(pb)
