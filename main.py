import os
import scratchattach as sa
# --- 設定情報 ---
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
session = sa.login('Kahu-tositai', PASSWORD)
project = session.connect_project("1442535436")
pb = sa.read_sb3_file("3DSplatoon.sb3")
project.set_body(pb)
