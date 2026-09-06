import io
import math
import requests
from PIL import Image

#URLの時間はテスト
# ターゲット情報（総画素数を2倍の4900に設定）
URL = "https://www.data.jma.go.jp/mscweb/data/himawari/img/jpn/jpn_trm_0020.jpg"
TARGET_TOTAL_PIXELS = 9800

# 指定された10色のパレット（1番目 〜 10番目）
COLOR_PALETTE = [
    "#0A1128",  # 1番目　濃い青
    "#102542",  # 2番目　ちょっと濃い青
    "#1E3A5F",  # 3番目　青
    "#878689",  # 4番目　青くも
    "#566270",  # 5番目　超薄い青
    "#CBD5E1",  # 6番目　白
    "#2D4A22",  # 7番目　濃い緑
    "#565E6A",  # 8番目　灰色青
    "#4A5112",  # 9番目　茶色
    "#57645C"   # 10番目　灰色
]

def hex_to_rgb(hex_str):
    """カラーコード（#RRGGBB）をRGBの数値（0-255）に変換する関数"""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

# 事前にパレットの色をRGB数値に変換しておく
PALETTE_RGB = [hex_to_rgb(c) for c in COLOR_PALETTE]

def find_closest_color_index(target_rgb):
    """一番近い色の「番目（1〜10）」を返す関数"""
    tr, tg, tb = target_rgb
    min_distance = float('inf')
    closest_index = 1
    
    # 10色すべてと距離を比べて、一番近いものを探す
    for idx, (pr, pg, pb) in enumerate(PALETTE_RGB):
        # 3次元空間の色距離（ユークリッド距離）の計算
        distance = math.sqrt((tr - pr)**2 + (tg - pg)**2 + (tb - pb)**2)
        if distance < min_distance:
            min_distance = distance
            closest_index = idx
            
    return closest_index

def main():
    print("画像をダウンロード中...")
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"エラー: 画像の取得に失敗しました (Status: {response.status_code})")
        return

    # 画像を読み込み
    img = Image.open(io.BytesIO(response.content))
    orig_w, orig_h = img.size

    # 総画素数が4900pxになるように幅と高さを計算 (アスペクト比を維持)
    aspect_ratio = orig_w / orig_h
    new_h = math.sqrt(TARGET_TOTAL_PIXELS / aspect_ratio)
    new_w = new_h * aspect_ratio

    # 整数に丸める
    new_w = round(new_w)
    new_h = round(new_h)

    print(f"リサイズ後のサイズ: {new_w}x{new_h} px (合計: {new_w * new_h} px)")

    # 画像を縮小、RGBモードに変換
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    rgb_img = resized_img.convert("RGB")

    # 各ピクセルをパレットの番号に変換
    result_matrix = []
    for y in range(new_h):
        row_indices = []
        for x in range(new_w):
            pixel_rgb = rgb_img.getpixel((x, y))
            # 一番近いパレットの「番目」を取得
            color_index = find_closest_color_index(pixel_rgb)
            row_indices.append(str(color_index))
        result_matrix.append("\n".join(row_indices))

    # 結果をテキストとしてまとめる（カンマと改行で区切る）
    output_text = "\n".join(result_matrix)

    # テキストファイルに保存
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(f"処理完了！結果を 'result.txt' に保存しました。")

if __name__ == "__main__":
    main()
