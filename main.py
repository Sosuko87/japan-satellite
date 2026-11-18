import os
import scratchattach as sa
# --- 設定情報 ---
USERNAME = "aideadasou"
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login('ZZZBanana', PASSWORD)
project = session.connect_project(1441978487)  # プロジェクトIDを指定
project.set_thumbnail(file="hello.gif")
