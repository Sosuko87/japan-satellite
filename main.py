import os
import time
import zipfile
import scratchattach as sa

PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login('Kahu-tositai', PASSWORD)
project = session.connect_project("1442732643")

failed_files = []
oversized_files = []

with zipfile.ZipFile("3DSplatoon.sb3", "r") as z:
    asset_files = [
        f for f in z.namelist()
        if f != "project.json" and not f.endswith("/")
    ]
    total = len(asset_files)
    print(f"全 {total} 個のアセットをアップロードします...")

    for i, filename in enumerate(asset_files, 1):
        data = z.read(filename)
        size_mb = len(data) / (1024 * 1024)

        # 10MB制限チェック
        if size_mb > 10:
            print(f"[{i}/{total}] ⚠️ サイズ超過 ({size_mb:.1f}MB): {filename}")
            oversized_files.append((filename, size_mb))
            continue

        asset_id, file_ext = filename.rsplit(".", 1)

        # 最大3回までリトライしながら送信
        success = False
        for attempt in range(3):
            try:
                session.upload_asset(
                    data,
                    asset_id=asset_id,
                    file_ext=file_ext.lower()
                )
                print(f"[{i}/{total}] OK: {filename}")
                success = True
                break
            except Exception as e:
                print(f"[{i}/{total}] 再試行中 ({attempt + 1}/3): {filename} ({e})")
                time.sleep(1.5)

        if not success:
            failed_files.append(filename)

        # サーバーに弾かれないよう少し待つ
        time.sleep(0.25)

print("\n--- 結果 ---")
print(f"10MB超えで弾かれたファイル: {len(oversized_files)}個")
for f, mb in oversized_files:
    print(f"  - {f} ({mb:.1f}MB)")

print(f"通信エラーで失敗したファイル: {len(failed_files)}個")
for f in failed_files:
    print(f"  - {f}")

pb = sa.read_sb3_file("3DSplatoon.sb3")
project.set_body(pb)
print("完了！")
