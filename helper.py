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
import base64
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

_ACT_TEMPLATE = """Start-Sleep -Milliseconds 1000
Add-Type -Name W -Namespace U -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);'
$sh = New-Object -ComObject WScript.Shell
for($i=0; $i -lt 6; $i++){
  $p = Get-Process __PROC__ -ErrorAction SilentlyContinue |
       Where-Object {$_.MainWindowHandle -ne 0} |
       Sort-Object StartTime -Descending | Select-Object -First 1
  if($p){
    [U.W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    if([U.W]::SetForegroundWindow($p.MainWindowHandle)){ break }
    try{ if($sh.AppActivate([int]$p.Id)){ break } }catch{}
  }
  Start-Sleep -Milliseconds 700
}"""


_TYPE_TEMPLATE = """Start-Sleep -Milliseconds 800
Add-Type -Name W -Namespace U -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow(); [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);'
$sh = New-Object -ComObject WScript.Shell
$ok = $false
for($i=0; $i -lt 12; $i++){
  $p = Get-Process claude -ErrorAction SilentlyContinue |
       Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
  if($p){
    [U.W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    [U.W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 400
    $fg = [U.W]::GetForegroundWindow(); $fgpid = 0
    [U.W]::GetWindowThreadProcessId($fg, [ref]$fgpid) | Out-Null
    if($fgpid -eq $p.Id){ $ok = $true; break }
    try{ $sh.AppActivate([int]$p.Id) | Out-Null }catch{}
  }
  Start-Sleep -Milliseconds 700
}
if($ok){
  Set-Clipboard -Value '__PHRASE__'
  Start-Sleep -Milliseconds 250
  $sh.SendKeys('^v')
  Start-Sleep -Milliseconds 450
  $sh.SendKeys('{ENTER}')
}"""


def send_to_claude_app(phrase):
    """Claudeアプリを前面化し、前面確認が取れた場合のみ依頼文を自動貼り付け+送信する。
    前面確認が取れなければ何も入力しない（他アプリへの誤入力防止）。"""
    subprocess.Popen(["explorer.exe", r"shell:appsFolder\Claude_pzs8sxrjxfjjc!Claude"])
    ps = _TYPE_TEMPLATE.replace("__PHRASE__", phrase.replace("'", "''"))
    b64 = base64.b64encode(ps.encode("utf-16-le")).decode()
    subprocess.Popen(["powershell.exe", "-WindowStyle", "Hidden", "-EncodedCommand", b64],
                     creationflags=subprocess.CREATE_NO_WINDOW)


def activate_later(proc_name):
    """指定プロセスのウィンドウを前面化する（ブラウザがフォアグラウンドを握っていると
    背面に開くため。最小化中でも復元する。ベストエフォート・失敗時はタスクバー点滅のまま）"""
    ps = _ACT_TEMPLATE.replace("__PROC__", proc_name)
    b64 = base64.b64encode(ps.encode("utf-16-le")).decode()
    subprocess.Popen(["powershell.exe", "-WindowStyle", "Hidden", "-EncodedCommand", b64],
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
        # /app/fanbox : Claudeアプリのチャットに「Fanbox下書き作って」を自動送信（2026-08-05 本人希望のゼロ操作方式）
        if path == "app/fanbox":
            try:
                send_to_claude_app("Fanbox下書き作って")
                return self._send(200, CLOSE_HTML, html=True)
            except Exception as e:
                return self._send(500, "error: " + str(e))
        if path.startswith("ws/"):
            name = path.split("/", 1)[1]
            if name not in WORKSPACES:
                return self._send(404, "unknown workspace: " + name)
            phrase = parse_qs(parsed.query).get("phrase", [""])[0]
            try:
                subprocess.Popen(ws_cmd(name, phrase or ""),
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
                activate_later("WindowsTerminal")
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
                if name == "claude":
                    activate_later("claude")  # 起動済みアプリの前面化がWindowsに拒否されるのを補う
                return self._send(200, CLOSE_HTML, html=True)
            except Exception as e:
                return self._send(500, "error: " + str(e))
        return self._send(404, "not found")


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8758), Handler).serve_forever()
