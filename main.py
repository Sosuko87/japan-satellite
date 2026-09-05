import io
import math
import requests
from PIL import Image
import datetime
import time
import os
import scratchattach as scratch

# --- 設定項目 ---
TARGET_TOTAL_PIXELS = 2400  # 👈 2400pxに修正（横56×縦42＝2352pxになります）
SCRATCH_PROJECT_ID = "あなたのプロジェクトID（数字）"

# 指定された10色のパレット（1番目 〜 10番目）
COLOR_PALETTE = [
    "#0A1128", "#102542", "#1E3A5F", "#FFFFFF", "#E2E8F0",
    "#CBD5E1", "#2D4A22", "#4D7C0F", "#78350F", "#A16207"
]

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

PALETTE_RGB = [hex_to_rgb(c) for c in COLOR_PALETTE]

def find_closest_color_index(target_rgb):
    tr, tg, tb = target_rgb
    min_distance = float('inf')
    closest_index = 1
    for idx, (pr, pg, pb) in enumerate(PALETTE_RGB):
        distance = math.sqrt((tr - pr)**2 + (tg - pg)**2 + (tb - pb)**2)
        if distance < min_distance:
            min_distance = distance
            closest_index = idx + 1
    return closest_index

def download_latest_image():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    rounded_minute = (now_utc.minute // 10) * 10
    base_time = now_utc.replace(minute=rounded_minute, second=0, microsecond=0)
    target_time = base_time - datetime.timedelta(minutes=10)

    for _ in range(12):
        time_str = target_time.strftime('%H%M')
        url = f"https://jma.go.jp_{time_str}.jpg"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        target_time -= datetime.timedelta(minutes=10)
    return None

def main():
    image_bytes = download_latest_image()
    if not image_bytes:
        print("エラー: 有効な画像が見つかりませんでした。")
        return

    img = Image.open(io.BytesIO(image_bytes))
    orig_w, orig_h = img.size

    # サイズ計算 (横56 x 縦42)
    new_w = round(math.sqrt(TARGET_TOTAL_PIXELS / (orig_w / orig_h)) * (orig_w / orig_h))
    new_h = round(math.sqrt(TARGET_TOTAL_PIXELS / (orig_w / orig_h)))
    
    print(f"リサイズ後のサイズ: {new_w}x{new_h} px (合計: {new_w * new_h} px)")
    
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    rgb_img = resized_img.convert("RGB")

    all_pixels_str = ""
    for y in range(new_h):
        for x in range(new_w):
            pixel_rgb = rgb_img.getpixel((x, y))
            color_index = find_closest_color_index(pixel_rgb)
            if color_index == 10:
                all_pixels_str += "0"
            else:
                all_pixels_str += str(color_index)

    # --- Scratch クラウド変数への送信処理 ---
    print("Scratchへのログインを試みています...")
    username = os.environ.get("SCRATCH_USERNAME")
    password = os.environ.get("SCRATCH_PASSWORD")
    
    if not username or not password:
        print("エラー: Scratchのログイン情報(Secrets)が設定されていません。")
        return

    try:
        session = scratch.login(username, password)
        conn = session.connect_cloud(project_id=SCRATCH_PROJECT_ID)
        
        # 2352文字を240文字ずつに分割（ちょうど10個の変数に収まります）
        chunk_size = 240  
        total_length = len(all_pixels_str)
        
        print(f"全 {total_length} 文字のデータを10分割して送信します...")
        
        var_count = 1
        for i in range(0, total_length, chunk_size):
            chunk = all_pixels_str[i:i+chunk_size]
            var_name = f"cloud_data_{var_count}"  # ☁ cloud_data_1 〜 ☁ cloud_data_10
            
            print(f"Scratchの ☁ {var_name} にデータを送信中... ({len(chunk)}文字)")
            conn.set_var(var_name, chunk)
            
            # 🛑 怒られないためのクールタイム（0.15秒待つ）
            time.sleep(0.15)
            var_count += 1
            
        print("🎉 すべてのクラウド変数（1〜10）への書き込みが安全に完了しました！")

    except Exception as e:
        print(f"Scratch連携エラー: {e}")

if __name__ == "__main__":
    main()
