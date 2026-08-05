# -*- coding: utf-8 -*-
"""ルーティンボード 窓口ヘルパー（127.0.0.1:8758 常駐）

ボード（strangearu.github.io/routine-board）の⚡ツールタブから、
ローカルツールやClaude窓口をワンタップ起動する。
スタートアップの「ルーティンボード-helper.lnk」→ pythonw.exe helper.py で常駐。
（旧まいにちクエストのhelper.pyを2026-08-05に移管。エンドポイント互換）

エンドポイント:
  GET /ping            → ok（死活確認）
  GET /ws/<name>?phrase=… → Claude窓口（会話継続 claude -c＋依頼文コピー）
  GET /launch/<name>   → TARGETS のコマンドを実行
"""
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

PROJECTS = r"C:\Users\stran\projects"
CLAUDE_EXE = r"C:\Users\stran\.local\bin\claude.exe"

# Claude窓口ワークスペース。flags: fanboxはChrome連携あり（下書き保存）、他は--no-chromeで軽量
WORKSPACES = {
    "zh":     {"dir": PROJECTS + r"\bilibili-zh",   "title": "bilibili中国語版の窓口", "flags": "--no-chrome"},
    "video":  {"dir": PROJECTS + r"\vlog-pipeline", "title": "動画の窓口",             "flags": "--no-chrome"},
    "fanbox": {"dir": PROJECTS + r"\fanbox-ops",    "title": "FANBOXの窓口",           "flags": "--chrome"},
}

def ws_cmd(name, phrase):
    w = WORKSPACES[name]
    fl = w.get("flags", "--no-chrome")
    ps = ("$host.UI.RawUI.WindowTitle='" + w["title"] + "'; "
          "Set-Clipboard -Value '" + phrase.replace("'", "''") + "'; "
          "Write-Host '=== " + w["title"] + " ===' -ForegroundColor Cyan; "
          "Write-Host '会話が開いたら Ctrl+V → Enter（依頼文はコピー済み）' -ForegroundColor Yellow; "
          "cd '" + w["dir"] + "'; "
          "& '" + CLAUDE_EXE + "' -c " + fl + "; "
          "if ($LASTEXITCODE -ne 0) { & '" + CLAUDE_EXE + "' " + fl + " }")
    return ["powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", ps]

def activate_console_later():
    """新しく開いたWindows Terminalを前面化する（ブラウザがフォアグラウンドを
    握っていると新規コンソールが背面に開くため。ベストエフォート・失敗時はタスクバー点滅のまま）"""
    ps = ("Start-Sleep -Milliseconds 1200; $sh=New-Object -ComObject WScript.Shell; "
          "for($i=0;$i -lt 6;$i++){ "
          "$wt=Get-Process WindowsTerminal -ErrorAction SilentlyContinue | "
          "Sort-Object StartTime -Descending | Select-Object -First 1; "
          "if($wt){ try{ if($sh.AppActivate([int]$wt.Id)){break} }catch{} }; "
          "Start-Sleep -Milliseconds 700 }")
    subprocess.Popen(["powershell.exe", "-WindowStyle", "Hidden", "-Command", ps],
                     creationflags=subprocess.CREATE_NO_WINDOW)


TARGETS = {
    # Claudeデスクトップアプリを起動/前面化（AUMID）
    "claude":   {"cmd": ["explorer.exe", r"shell:appsFolder\Claude_pzs8sxrjxfjjc!Claude"]},
    # 各ツールは自前のrun.batが「起動済みなら開くだけ」を面倒みてくれる
    "retouch":  {"bat": PROJECTS + r"\retouch-studio\run.bat"},
    "eventkit": {"bat": PROJECTS + r"\event-kit\run.bat"},
    "tracker":  {"bat": PROJECTS + r"\sns-tracker\run.bat"},
}


CLOSE_HTML = ("<!doctype html><meta charset='utf-8'><title>OK</title>"
              "<body style='font-family:sans-serif;font-size:13px'>起動しました。この窓は自動で閉じます"
              "<script>setTimeout(function(){window.close()},400)</script></body>")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # 静かに
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        # ChromeのPrivate Network Access(ローカルネットワーク保護)のプリフライト対策
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def _send(self, code, body, html=False):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", ("text/html" if html else "text/plain") + "; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        if path == "ping":
            return self._send(200, "ok")
        if path.startswith("ws/"):
            name = path.split("/", 1)[1]
            if name not in WORKSPACES:
                return self._send(404, "unknown workspace: " + name)
            phrase = parse_qs(parsed.query).get("phrase", [""])[0]
            try:
                subprocess.Popen(ws_cmd(name, phrase or ""),
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
                activate_console_later()
                return self._send(200, CLOSE_HTML, html=True)  # 窓ナビゲーション起動時に自動で閉じる
            except Exception as e:
                return self._send(500, "error: " + str(e))
        if path.startswith("launch/"):
            name = path.split("/", 1)[1]
            t = TARGETS.get(name)
            if not t:
                return self._send(404, "unknown target: " + name)
            try:
                if "bat" in t:
                    subprocess.Popen(
                        ["cmd", "/c", "start", "", t["bat"]],
                        creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen(t["cmd"], creationflags=subprocess.CREATE_NO_WINDOW)
                return self._send(200, CLOSE_HTML, html=True)
            except Exception as e:
                return self._send(500, "error: " + str(e))
        return self._send(404, "not found")


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8758), Handler).serve_forever()
