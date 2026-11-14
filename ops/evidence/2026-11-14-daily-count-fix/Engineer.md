# Engineer：日次復習の開始前問数修正

担当 `engineer_daily_count_fix`。2026-11-14。統括がlease取得とPdM範囲確認後、独立checkout `/workspace/yuika-daily-fix-20261114` で既存PR10の `132f9f59ebd23b6dab33e7d1e23bf4d077b8070d` から実装。push・台帳編集なし。

## 固定候補

`55435567d44f05dc35f3ea6d73c4ba9cac2dc496`、commit後cleanへ固定。独立QAに引き渡した後は編集しない。

基点相対9ファイル: `scripts/practice/adaptive.js`、応仁/鎌倉/平安/重点復習の4HTML、`assets/design.js`、`scripts/check_all.sh`、`tests/daily_count.py`、README。

## 動作

- 期限到来・弱点・通常の候補集合を共有する `dailySources` と、originId/idの一意件数を上限で切る `dailyCount` を追加。表示時のshuffle・dailyQuestions呼出しはなく乱数を消費しない。
- 日次選定は従来どおり期限→弱点→shuffleした通常、origin重複除去、既存問数上限。選定・件数・利用不能判定には呼出内で同じnowを渡す。既存呼出し方も維持。
- 対象4ページの入口は「今日の復習をはじめる（今回は実数問）」、0件は無効。0件説明と利用不能説明を別にし、日次status要素がある場合だけ共通デザインの移動後もボタン直後に配置する。
- クリック直前の利用不能は再描画して停止。表示件数と現在件数が異なる場合は問数を更新し、抽選・セッション開始・回答保存をせず再確認を求める。既存の明示 `?daily=1` 導線は描画済み件数と一致するため1回で開始する。
- `MODES.daily`の表示名や共通adaptive内の時刻警告は「今日の復習」に整合し、永続mode値dailyは変えない。既存推薦、採点、保存・問題ID/版、通知、storageイベント処理は変更しない。
- 理科とトップは今回対象外。既存のstorageイベント未配送・キー削除を含む完全同期を追加したものではない。

## 実行済み検証

生成順 `python scripts/practice/embed.py` → `python scripts/design/build_summary.py` → `python scripts/design/embed.py` → `python scripts/parent/embed.py` は終了0。summary projection、index、理科、生成器本体には基点相対差分なし。

`python tests/daily_count.py` 初回はテスト側のrandomOriginalをnavigation前のwindowにだけ保存しており、再読込み後に参照してReferenceError。製品エラーではない。テストにその呼出内のMath.randomを局所保持する修正を1回行い、2回目は終了0。

- 抽出した固定基点の日次関数との36合成ケース: 候補0/1/4/5/9/20 × 上限5/10/15 × 利用可能/不能。期限/弱点/通常の重複集合でID順・抽選回数・表示件数一致を確認。
- Chromium768×1024の実4ページ: 初期5問、home描画による乱数/回答記録書込みなし、実開始5問、明示daily導線、件数が5→10へ変わる直前条件の再確認と抽選なし、dirty停止、visible status。
- 実UIのC=応仁4問、D=応仁0で無効・説明可視・直接開始拒否、E=平安2問を確認。UIにない平安15はUI試験に使わず、5/10/15は純粋ロジックの上限試験として区別。

ログ `/tmp/yuika-daily-fix-focused1.log` と `/tmp/yuika-daily-fix-focused2.log`。最終候補前の同一製品内容によるfocused試験であり、固定HEAD全25suite・独立安全境界の受入はQA担当が別途行う。`git diff --check` 成功。

## 未完了・限界

この引渡し時点では全25suite、独立QAによる実回答→採点→保存→再読込、親モード、読取拒否・未来時刻、時刻/既存storageイベントの確認結果はまだない。既存の検証済みvenvを手動利用した環境で、自動snapshot引継ぎ成功とは扱わない。合成データだけを使い、Safari/実iPad/本人試用/学習効果/公開環境は未検証。デプロイ・main merge・外部送信・Secrets/権限変更なし。
