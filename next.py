import scratchattach as sa
import os
import time
import datetime
import sys

#sys.exit()
now = datetime.datetime.now()

if not 15 <= now.minute <= 18:
    print("強制終了します")
    sys.exit()

ad_project = 1392601120
USERNAME = '-TREND_FLOW-'
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login(USERNAME, PASSWORD)
cool_time=0


with open("studio.txt", "r", encoding="utf-8") as f:
    for raw_line in f:
        studio_id = str(raw_line).strip()
        if not studio_id or not studio_id.isdigit():
            continue
            
        print(f"スタジオ {studio_id} に接続中...")
        
        try:
            studio = session.connect_studio(studio_id)
            studio.remove_project(ad_project)
            studio.add_project(ad_project)
            print(f"スタジオ {studio_id} の更新に成功しました。")
            
        except Exception as e:
            print(f"スタジオ {studio_id} でエラーが発生しました: {e}")
            
        time.sleep(5)
