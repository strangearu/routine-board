# -*- coding: utf-8 -*-
r"""fanbox_assets.json（文体プロンプト+テンプレバンク）を暗号化して fanbox_assets.enc.json に書き出す。

使い方: fanbox_assets.json を更新したら
  python encrypt_fanbox.py
→ git add fanbox_assets.enc.json → commit → push で公開反映。
復号はハブと同じパスコード（fanbox.html が localStorage 'hub-pass' で自動復号）。
平文の fanbox_assets.json は .gitignore 済み＝コミット禁止（文体プロファイルは非公開資産）。
"""
import json, base64, hashlib, io, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fanbox_assets.json")
OUT = os.path.join(HERE, "fanbox_assets.enc.json")
PASS_FILE = r"C:\Users\stran\.claude\secrets\hub-pass.txt"
ITER = 200000

data = json.loads(io.open(SRC, encoding="utf-8").read())  # 壊れたJSONを公開しない
payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

passcode = io.open(PASS_FILE, encoding="utf-8").read().strip().lstrip("\ufeff")
salt = os.urandom(16)
iv = os.urandom(12)
key = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, ITER, dklen=32)
ct = AESGCM(key).encrypt(iv, payload, None)

io.open(OUT, "w", encoding="utf-8").write(json.dumps({
    "salt": base64.b64encode(salt).decode(),
    "iv": base64.b64encode(iv).decode(),
    "iter": ITER,
    "ct": base64.b64encode(ct).decode(),
}))
print("encrypted fanbox assets ->", OUT)
