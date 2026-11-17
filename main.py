import os
import scratchattach as sa
# --- 設定情報 ---
USERNAME = "aideadasou"
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login(USERNAME, PASSWORD)
comment_studio = 52164171
studio = session.connect_studio(comment_studio)
studio.post_comment("こんにちは！")
