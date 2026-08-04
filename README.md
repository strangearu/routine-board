# ルーティンボード

毎日のやること・ルーティン（毎日/毎週/毎月）・⚡Claude窓口を1画面にした統合ボード。
旧「まいにちクエスト」の後継（2026-08-05一本化）。
公開URL: https://strangearu.github.io/routine-board/ （PC・スマホ共通）

## タブ構成
- **きょう** — きょうのポイント → ⭐最優先 → ⏰しめ切り → 📌きょうの担当ルーティン（毎週/毎月から自動抽出）→ 📅予定 → 💡提案 → 🔁毎日
- **ルーティン** — 毎日・毎週（曜日チップ）・毎月のカタログ
- **⚡ツール** — Claude窓口（中国語版/動画/FANBOX）・ツール起動（レタッチ/トラッカー/撮影会キット）・リンク・自動運転一覧

## 仕組み
- 毎朝8:00の scheduled-task **daily-task-brief** が `brief.json` を生成
  → `python encrypt_brief.py` で `brief.enc.json` に暗号化 → git push で自動反映
- 復号はハブ（sns-tool）と同じパスコード。同一オリジンなので localStorage `hub-pass` を共有
- `brief.json`（平文）は **.gitignore 済み＝絶対にコミットしない**
- チェック状態は端末ごと（localStorage）。**論理日=あさ6時切り替え**（夜型対応）で日/週/月リセット
- 期限の「あとX日」はアプリ側で毎日再計算
- `helper.py` = 127.0.0.1:8758 常駐（スタートアップ「ルーティンボード-helper.lnk」）。
  ⚡ツールタブから `/ws/…`（claude -c 会話継続+依頼文コピー）と `/launch/…` を呼ぶ。PC専用

## 起動導線
- PCログイン時: スタートアップ「ルーティンボード.lnk」（chrome --app）+ helper.lnk
- スマホ: URLを開いて「ホーム画面に追加」（専用アイコンあり）

## 手動更新・開発
```
python encrypt_brief.py
git add brief.enc.json
git commit -m "brief更新"
git push
```
- アイコン再生成: `python make_icons.py`
- デモ表示（実データなし）: https://strangearu.github.io/routine-board/?demo=1
- ローカル検証: launch.json「routine-board-check」（http://127.0.0.1:8759）
