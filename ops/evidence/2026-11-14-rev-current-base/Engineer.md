# Engineer: PR10 現行基盤への互換性統合

Engineer: engineer_rev_current。2026-11-14。独立checkout `/workspace/yuika-rev-current-20261114`。PdM案をPrMが受入後に実装。pushなし。

## 候補

固定clean候補 `132f9f59ebd23b6dab33e7d1e23bf4d077b8070d`。両親は元PR10 `ba829a1176ff1ead7d312526890afe8792178c99` とmain `86514eda054a5a2e09204df3a0668e40624c16de`。mainをdraft topicへ取り込む履歴保持の統合で、本番mainへのmergeではない。2 HTML競合を解消した。

main相対変更はREADME.md、assets/design.js、onin-review.html、kamakura-review.html、scripts/check_all.sh、tests/recommended_review.py、tests/review_entry.pyの7ファイル。

## 実装

元PR10のおすすめA/B/C交互選定、元問題だけの履歴、フィルター、開始時理由固定、候補不足時の実数を維持。現在mainの親モードstorage、prototype名前空間、問題版validator、採点/回答保存/日次/弱点/期限実装を維持した。home統合では元問題IDへ戻す現在mainの統計とadaptivePanelを保った。

おすすめは現在mainのpracticeUnavailable(data.events, now)でblocked/dirty/5分超未来を停止。正常0候補と休止を別表示し、開始にも同じガードがかかる。<=5分の未来は元推薦契約の事実理由だけを維持し、24時間経過としない。設定保存はmain既存rememberPrefsを使用。

assets/design.jsの条件付き1行で、おすすめ要素がある両ページだけ共通statsの直後に既存案内を移動。既存日次入口・通常練習を置換しない。新ページや新推薦先を追加していない。

生成器はdesign/embed.py→parent/embed.pyを実行。heian/mock-focus/理科/トップにmain相対差分なし。両HTMLのADAPTIVE/PROTOTYPEブロックとsubmit/load関連の一致を静的照合。adaptive.js、親runtime、保存validator、通知/CSPを変更していない。日次件数の不一致は未修正。

## 実行済み検証

- 推薦focused初回は合成fixtureのquestionVersionにVERSIONを入れ、現在validatorが「対応していない問題ID・問題版」で拒否。製品validatorは正常に拒否しており弱めていない。
- fixtureを既存currentQuestionVersion(q)へ直した2回目 `python tests/recommended_review.py` は応仁/鎌倉とも成功、POST到達0。
- `python tests/review_entry.py` 初回成功。両単元768×1024、候補あり/0/休止、設定追従、keyboard/focus、開始/採点/保存/再読込、横はみ出しなしを確認。
- `git diff --check` 成功。最終候補をcommit後cleanへ固定して独立QAへ引き渡した。Engineer実行のfocused試験はcommit直前の同一候補内容であり、最終HEAD全suiteの証拠は独立QAが別に実行する。

旧PR10テストの静的一致基準は現mainへ更新し、元の旧validator互換性確認も残した。旧validatorへ渡す合成normal eventだけ新しい任意questionVersionを除去して旧形状を検証する（製品保存や移行ではない）。現在のprototype JSON envelopeとimport案内へ追従し、重複なし/回答保持/旧キーsentinel不変を維持。未来の元1時間後ケースは<=5分の事実理由テストへ分離し、別に1時間後の休止assertを追加。公開font CSS GETは遮断して許容種別を限定し、POST禁止は維持。

ログ: `/tmp/yuika-rev-recommended-first.log`、`/tmp/yuika-rev-recommended-second.log`、`/tmp/yuika-rev-entry-first.log`。

## 限界

QA引渡し時点で全24suite・独立追加親モード/保存失敗検証は未実施。実機Safari/iPad、本人試用、公開環境、学習効果は未検証。依存は既存検証済みvenvの手動再利用であり、自動snapshot引継ぎ成功ではない。私的入力・本番merge・公開/デプロイ・実通知・権限変更なし。
