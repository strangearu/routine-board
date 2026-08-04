# -*- coding: utf-8 -*-
r"""brief.json を暗号化して brief.enc.json に書き出す（ルーティンボード用）。

使い方: brief.json を更新したら
  python encrypt_brief.py
→ そのあと git add brief.enc.json → commit → push で公開反映。
復号はハブと同じパスコード（index.html が localStorage 'hub-pass' で自動復号）。
方式は manager-ops\encrypt_reports.py と同一（PBKDF2 200k + AES-GCM）。
"""
import json, base64, hashlib, io, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brief.json")
OUT = os.path.join(HERE, "brief.enc.json")
PASS_FILE = r"C:\Users\stran\.claude\secrets\hub-pass.txt"
ITER = 200000

raw = io.open(SRC, encoding="utf-8").read()
data = json.loads(raw)  # JSONとして壊れていたらここで止まる（壊れたデータを公開しない）
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
print("encrypted brief (generated=%s) -> %s" % (data.get("generated"), OUT))
