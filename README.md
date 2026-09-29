# ルーティンボード

毎日のやること・ルーティン（毎日/毎週/毎月）・⚡Claude窓口を1画面にした統合ボード。
旧「まいにちクエスト」の後継（2026-08-05一本化）。
公開URL: https://strangearu.github.io/routine-board/ （PC・スマホ共通）

## タブ構成（v3: Asana/Sharegantt風ライトデザイン・ライト/ダーク切替🌙）
- **ボード** — PC=カンバン4列（⏰しめ切り／📌きょうやること／💡やるといいこと／📅よてい）、スマホ=1列縦積み。⭐最優先は金縁カードで先頭
- **カレンダー** — PC=月グリッド、スマホ=日付リスト。Googleカレンダー「るあ」から毎朝取得（brief.jsonのschedule=30日分・メモ欄は含めない）
- **ルーティン** — 毎日・毎週（曜日チップ）・毎月のカタログ（PC=3列）
- **⚡ツール** — Claude窓口（中国語版/動画/FANBOX）・ツール起動（レタッチ/トラッカー/撮影会キット）・リンク・自動運転一覧

## 仕組み
- Task Scheduler **RoutineBoardDailyBrief**（ログオン時＋毎朝8:05）が `scripts\daily_brief_kick.ps1` を実行し、
  古い時だけ `brief.json` を生成 → `python encrypt_brief.py` で `brief.enc.json` に暗号化 → git push で自動反映
- **画面は自動で最新になる（2026-09-28）**: きょうの分が未着の間は1分おき、届いた後は5分おきに `brief.enc.json` を確認し、
  変わっていたら開きっぱなしでも中身を入れ替える（画面に戻ってきた時・あさ6時をまたいだ時も確認）。
  未着の間は上部に案内バナーが出る。マネージャーハブ（sns-tool）の「今日」タブにも同じデータが出る
- 復号はハブ（sns-tool）と同じパスコード。同一オリジンなので localStorage `hub-pass` を共有
- `brief.json`（平文）は **.gitignore 済み＝絶対にコミットしない**
- チェック状態は端末ごと（localStorage `rb-checks`）。**論理日=あさ6時切り替え**（夜型対応）で日/週/月リセット。
  保存先はマネージャーハブの「きょうのブリーフ」と共用＝同じ端末・同じブラウザなら、どちらで付けても両方に反映される
- 期限の「あとX日」はアプリ側で毎日再計算
- `helper.py` = 127.0.0.1:8758 常駐（スタートアップ「ルーティンボード-helper.lnk」）。
  ⚡ツールタブから `/ws/…`（claude -c 会話継続+依頼文コピー）と `/launch/…` を呼ぶ。PC専用

## 起動導線
- PCログイン時: スタートアップ「ルーティンボード.lnk」+ helper.lnk
  - **開く順番（2026-09-28変更）**: ショートカットは画面を直接開かず、`scripts\open_board_when_fresh.ps1` を呼ぶ。
    このスクリプトが ①ブリーフ生成をすぐ開始 → ②きょうのブリーフ完成を待つ → ③公開先に届いたのを確認 → ④画面を開く。
    生成が失敗した時・20分たっても終わらない時は、待たずに開く（画面側の案内バナーと自動更新が引き継ぐ）
  - 以前は画面が生成より5〜10分早く開き、毎朝「前日のまま」が最初に表示されていた
  - 結果は `scripts\state\open_board.log`（`OK open board`=最新で開いた／`WARN open board`=古い状態で開いた＋理由）
  - 元のショートカットの控え: `scripts\state\startup_backup_20260928\`
- デスクトップ「ルーティンボード.lnk」は今まで通りすぐ開く（手動で開く用）
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
- 起動スクリプトの試運転: `powershell -File C:\Users\stran\scripts\open_board_when_fresh.ps1 -DryRun`（画面を開かずに判定だけ行う）
