# ルーティンボード

毎日のやること・毎日/毎週/毎月のルーティンを1画面で見る＋チェックできるボード。
公開URL: https://strangearu.github.io/routine-board/ （PC・スマホ共通）

## 仕組み
- 毎朝8:00の scheduled-task **daily-task-brief** が `brief.json` を生成
  → `python encrypt_brief.py` で `brief.enc.json` に暗号化 → git push で自動反映
- 復号はハブ（sns-tool）と同じパスコード。同一オリジンなので localStorage `hub-pass` を共有
  （ハブで一度パスコードを入れた端末なら入力不要）
- `brief.json`（平文）は **.gitignore 済み＝絶対にコミットしない**。公開されるのは暗号化済み `brief.enc.json` のみ
- チェック状態は端末ごと（localStorage）。毎日分は日付で、毎週分は週で、毎月分は月で自動リセット
- 期限の「残りX日」はアプリ側で毎日再計算（データ更新が止まっても日数は正しい）

## 手動更新
```
python encrypt_brief.py
git add brief.enc.json
git commit -m "brief更新"
git push
```

## デモ表示（レイアウト確認用・実データなし）
https://strangearu.github.io/routine-board/?demo=1
