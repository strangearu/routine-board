# -*- coding: utf-8 -*-
"""ルーティンボードのアイコン一式を生成（PIL）。
紫→ピンクのグラデ角丸に、白いボード＋チェックリスト3行（1行目チェック済み）。
出力: icon-512.png / icon-192.png / apple-touch-icon.png(180) / favicon-32.png / app.ico
"""
from PIL import Image, ImageDraw
import os

HERE = os.path.dirname(os.path.abspath(__file__))
S = 512


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


def make_base():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # 斜めグラデ背景（紫#8b7cf6→ピンク#f67cb2）
    grad = Image.new("RGBA", (S, S))
    c1, c2 = (139, 124, 246), (246, 124, 178)
    px = grad.load()
    for y in range(S):
        for x in range(S):
            t = (x + y) / (2 * S - 2)
            px[x, y] = (round(c1[0] + (c2[0] - c1[0]) * t),
                        round(c1[1] + (c2[1] - c1[1]) * t),
                        round(c1[2] + (c2[2] - c1[2]) * t), 255)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=112, fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)
    # 白ボード（クリップボード風・上部にクリップ）
    bx0, by0, bx1, by1 = 96, 120, 416, 448
    d.rounded_rectangle([bx0 + 6, by0 + 10, bx1 + 6, by1 + 10], radius=36, fill=(0, 0, 0, 46))  # 影
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=36, fill=(255, 255, 255, 255))
    # クリップ
    d.rounded_rectangle([S // 2 - 74, 84, S // 2 + 74, 152], radius=26, fill=(58, 48, 106, 255))
    d.rounded_rectangle([S // 2 - 46, 104, S // 2 + 46, 138], radius=14, fill=(255, 255, 255, 255))

    # チェックリスト3行
    rows = [(200, True), (280, False), (360, False)]
    for cy, checked in rows:
        cb = [128, cy - 26, 180, cy + 26]  # チェックボックス
        if checked:
            d.rounded_rectangle(cb, radius=14, fill=(94, 214, 162, 255))
            d.line([(139, cy + 2), (152, cy + 15), (172, cy - 13)], fill=(255, 255, 255, 255), width=11, joint="curve")
        else:
            d.rounded_rectangle(cb, radius=14, outline=(160, 150, 220, 255), width=9)
        # テキスト線
        line_col = (196, 188, 235, 255) if not checked else (216, 210, 244, 255)
        d.rounded_rectangle([204, cy - 13, 384, cy + 13], radius=13, fill=line_col)
    return img


base = make_base()
base.save(os.path.join(HERE, "icon-512.png"))
base.resize((192, 192), Image.LANCZOS).save(os.path.join(HERE, "icon-192.png"))
base.resize((180, 180), Image.LANCZOS).save(os.path.join(HERE, "apple-touch-icon.png"))
base.resize((32, 32), Image.LANCZOS).save(os.path.join(HERE, "favicon-32.png"))
base.save(os.path.join(HERE, "app.ico"),
          sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icons written")
