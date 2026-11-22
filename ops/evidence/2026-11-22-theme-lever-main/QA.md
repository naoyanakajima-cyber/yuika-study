# THEME-MVP 新mainてこ互換性 — 独立QA

担当 `qa_theme_lever`。対象は固定 `e89aa335936508c6e4984c523ec65da97f510cbd`、独立detached `/workspace/qa-theme-lever-checkout`。旧テーマHEAD `9fc4bbf3e6c72e09327b6610338f12937fc7aba5` とmain `58f8b53b4da69806d15a126fc525b65893a0bf35` の両履歴を持つ。実装者とは別担当が対象revisionを直接検証した。実データ・実通知・push・本番merge/deploy・設定変更なし。

## 静的レビュー

`static-review.json`：mainとの差はREADME、theme-spec、鎌倉HTML、必須suite登録、themeテストの5 filesのみ。鎌倉HTML/theme test/specは旧テーマ候補とbyte一致。他全tracked filesはmain同一で、共有design.css/design.js、理科HTML、生成器、履歴archiveも含む。main26 suiteにtheme_reviewだけを加えた27 suiteを集合比較した。てこ図生成関数・ラベル寸法・28問・段階制御・採点/保存などのmain契約をテーマの都合で変更していない。

## 限定UI：初回成功

`probe.py` / `probe-attempt1.log` / `probe-result.json`。Chromium、768×1024、fresh contexts、固定乱数、合成データ、通知遮断CSPのPreviewHandler。通常/親各5問（text3/choice2）の同一runで、入力/選択後、hint後、採点後、結果で標準/鎌倉切替と標準復帰。run/data/prefs、学習DOM、入力、notice/blocked/dirtyは切替前後不変。テーマ操作が変更可能なlocalStorageは通常のテーマキーだけで、親は本人localStorage全体不変。回答後再読込で各5eventsを維持した。結果後spyをresetしてテーマ切替由来enqueue 0、操作由来resource要求0。全probeのPOST要求/到達0、pageerror0、既存外部font GET 16件を遮断。全suiteの模擬APIとは区別し、全通信0とは主張しない。

通常/親の同origin往復で、テーマキーを標準→鎌倉→標準と保存し、対象外の理科lever-01/27/28を同じ問題として表示。SVG innerHTML/viewBox/computed文字色・サイズ・太さ・相対位置/線色・太さ/図寸法が3状態間で完全一致。理科にtheme UI/data属性なし、横overflowなし。合成の対象queueで代表図を出しており、このprobeで挑戦解放を操作したとは主張しない（既存lever suiteの担当）。

鎌倉模式図の将軍/執権2ラベルを候補で計測。標準/鎌倉×screen/printの全4組で白13px文字/背景rgb(143,79,60)、contrast **6.265720821251096**。旧候補の数値転記ではなく今回computed実測。図DOMはmedia切替前後不変。

`visual-review.json`に実際に開いた12画像を列記。通常/親の標準/鎌倉home、入力済hint、模式図screen/print代表、てこ基本図・台＋ばねばかり・吊り下げ支点を目視。支点・おもり・距離・ばねばかりラベルに欠け/重なりを認めない。画面全体の全状態pixel一致や28問全面再校閲は行っていない。

## 保存障害等の既存必須suite対応

追加probeで過去の全障害試験を重複させず、候補の `tests/theme_review.py` の実行へ対応付ける。

| 境界 | 具体assert |
|---|---|
| 未知値を保持・標準fallback・起動で書込なし | 227–232行、unknown/JSON/空文字を保持しthemeWrites=0 |
| get例外で標準・学習開始可 | 233–236行、blocked false/themeWrites=0/start後check表示 |
| set例外・学習警告維持・回復 | 237–249行、専用status、state不変、テーマキー未保存、標準復帰後fault解除でstatus空、notice保持 |
| 親session保存/再読込/終了 | 250–266行、本人disk不変、専用sessionキー復元、終了で通常テーマ復帰/session領域消去 |
| session拒否時の一時領域 | 267–277行、親表示・メモリtheme保持・本人disk不変・reloadで標準 |

既存suiteではkeyboard/44px/8px/print/非対象画面/contrast等も実行する。追加probeで独自に再測定しない項目はその証拠へ帰属させる。

## 生成器制約と検証限界

Engineerが7本の生成列を実行し、理科HTMLのてこ固有処理/answerUnit・answerTagの欠落を観測し、候補に採用していない。embed_science/prototypeを含む生成器sourceと理科targetはmainと同一で、QAもそのbyte一致を独立確認した。個別scriptの因果は未切分け、main単独再実行なし。QA自身の再生成再現も行っていない。これはテーマ差分による退行とは分け、全生成パイプライン整合成功と報告しない。design summary/embed/parent冪等性の実行はEngineer証拠に帰属する。

既存 `/workspace/yuika-study/.venv` の手動再利用。自動snapshot復元成功ではない。初回static clean判定はruntime-only `.venv` symlinkをuntrackedと検知した。tracked変更なし、ignored `.venv/bin` linkに直した2回目static確認は成功。全suiteの冒頭にそのuntracked runtime entryを保持、前後HEADと最終cleanを別保存する。詳細 `harness-notes.md`。製品assert緩和/同原因3回目/無根拠な全suite再実行なし。

実機iPad/Safari/WebKit/native zoom・本人嗜好・学習効果・実プリンター・公開動作は未検証。新mainの内容の全面再校閲は既存テストを超えて行っていない。

## 必須suite結果

**初回27/27成功、exit 0、323秒。** 固定HEADは前後一致、最終 `git status --short` 空。製品tracked filesは前後clean。全suite冒頭のruntime-only link記録は上述の通り。合成試用向けテーマ/main互換性の受入範囲は合格。生成列制約・実機/本人嗜好/公開の未検証を解除するものではない。

`check-all-attempt1.log` / `final-result.json`に全結果。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 5 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 12 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 6 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 4 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 18 |
| `tests/lever.py` | 0 | 5 |
| `tests/microscope.py` | 0 | 24 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 3 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 12 |
| `tests/parent_mode.py` | 0 | 20 |
| `tests/design_c.py` | 0 | 20 |
| `tests/responsive_subjects.py` | 0 | 116 |
| `tests/theme_review.py` | 0 | 12 |
