import io
import os
import math
import requests
from PIL import Image
import scratchattach as sa
import time
from datetime import datetime, timezone


utc_now = datetime.now(timezone.utc)

# 2. 「分」を10の倍数に切り捨てる計算
# （例：23分 // 10 = 2  ->  2 * 10 = 20分）
rounded_minute = (utc_now.minute // 10) * 10

# 3. 分を置き換えて、秒とマイクロ秒を0にする
new_utc = utc_now.replace(minute=rounded_minute, second=0, microsecond=0)
use_utc = new_utc.strftime("%H%M")
print(use_utc)
# --- 設定情報 ---
USERNAME = os.environ.get("SCRATCH_USERNAME")
PASSWORD = os.environ.get("SCRATCH_PASSWORD")
PROJECT_ID = "1380167146"

URL = f"https://www.data.jma.go.jp/mscweb/data/himawari/img/jpn/jpn_trm_{use_utc}.jpg"
print(f"画像URL: {URL}")
TARGET_TOTAL_PIXELS = 2500

COLOR_PALETTE = [
    "#0A1128", "#102542", "#1E3A5F", "#102201", "#25390b",
    "#aea8a8", "#000000", "#384228", "#717871", "#d8d2d4"
]

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

PALETTE_RGB = [hex_to_rgb(c) for c in COLOR_PALETTE]

def find_closest_color_index(target_rgb):
    tr, tg, tb = target_rgb
    min_distance = float('inf')
    closest_index = 0
    
    for idx, (pr, pg, pb) in enumerate(PALETTE_RGB):
        distance = math.sqrt((tr - pr)**2 + (tg - pg)**2 + (tb - pb)**2)
        if distance < min_distance:
            min_distance = distance
            closest_index = idx  # 0から9の数値を返す
            
    return closest_index

def main():
    print("Scratchにログイン中...")
    try:
        session = sa.login(USERNAME, PASSWORD)
        connection = session.connect_cloud(PROJECT_ID)
        print("Scratchへのログインとクラウド接続に成功しました！")
    except Exception as e:
        print(f"ログインエラー: {e}")
        return

    print("画像をダウンロード中...")
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"エラー: 画像の取得に失敗しました")
        return

    img = Image.open(io.BytesIO(response.content))
    crop_box = (185, 51, 679, 489)
    cropped_img = img.crop(crop_box)
    crop_w, crop_h = cropped_img.size

    aspect_ratio = crop_w / crop_h
    new_h = round(math.sqrt(TARGET_TOTAL_PIXELS / aspect_ratio))
    new_w = round(new_h * aspect_ratio)

    print(f"リサイズサイズ: {new_w}x{new_h} px")

    resized_img = cropped_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    rgb_img = resized_img.convert("RGB")

    # 1. 数字だけを確実につなげる
    all_pixels_chars = ""
    for y in range(new_h):
        for x in range(new_w):
            pixel_rgb = rgb_img.getpixel((x, y))
            color_index = find_closest_color_index(pixel_rgb)
            # 確実に0〜9の1文字の文字列にする
            all_pixels_chars += str(color_index)

    # 2. 10等分の処理
    total_length = len(all_pixels_chars)
    n = 10
    chunk_size = total_length // n
    remainder = total_length % n

    cloud_data = {}
    start = 0

    for i in range(n):
        end = start + chunk_size + (1 if i < remainder else 0)
        var_name = f"cloud_data_{i+1}"
        
        # 切り出した文字列
        chunk_value = all_pixels_chars[start:end]
        
        # 【超重要】念のため、空白や改行を完全に排除し、数字だけにするガード
        chunk_value = "".join(c for c in chunk_value if c.isdigit())
        
        cloud_data[var_name] = chunk_value
        start = end

    # 3. Scratchのクラウド変数を自動更新
    print("\nクラウド変数をまとめて更新中...")
    try:
        # 10個の変数をいっきにまとめてScratchに送信します
        connection.set_vars(cloud_data)
        print("すべてのクラウド変数の送信コマンドを完了しました！")
    except Exception as e:
        print(f"エラー: 更新に失敗しました。理由: {e}")
        
    print(f"\n処理完了！ブラウザのScratch画面を一度「再読み込み（リロード）」して確認してください。")

    #ここから他の処理に入る
    with open("studio.txt", "r", encoding="utf-8") as f:
        for raw_line in f:
            # 強制的に文字列(str)に変換してから空白・改行を取り除く
            studio_id = str(raw_line).strip()
        
        # 空行、または正しくないID（文字が含まれるなど）はスキップする
            if not studio_id or not studio_id.isdigit():
                continue
            
            print(f"スタジオ {studio_id} に接続中...")
        
            try:
                # 3. スタジオIDで接続する
                studio = session.connect_studio(studio_id)
            
                # 一度削除して、新しく追加（スタジオの先頭に上げる処理）
                studio.remove_project(1350622697)
               studio.add_project(1350622697)
                print(f"スタジオ {studio_id} の更新に成功しました。")
            
            except Exception as e:
                print(f"スタジオ {studio_id} でエラーが発生しました: {e}")
            
        # Scratchの制限回避のため、3秒待つ
            time.sleep(3)
    

main()




