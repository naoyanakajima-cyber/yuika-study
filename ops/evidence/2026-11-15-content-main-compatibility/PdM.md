# CONTENT-MVP：現mainへの限定互換性追従

PdM `pdm_content_trial_delivery`、2026-11-15。運用正本c1fa98cとlease取得214df00136da7edb237d503888d43cb331d7cbfdの台帳/運用規則、content-spec/content-try-spec、指定gitオブジェクトを読み取り照合した。runはcycle-20261115T090232Z。製品基点は既存PR11 ee51e68d7e1eeb21bd0e959ec58166a869947d0a、追従対象mainは60d1a946cc02ed8acea54c0d7af7d6451fcc30ec。製品編集・テスト・push・ops変更なし。

## 目的と必要性

保護者役のテスターが、現行の学習画面と同じ候補環境で、合成教材を確認し「保存しない試し解き」で問題文/許容表記/ヒント/解説を点検できる状態を保つ。今回の価値は教材確認機能の追加ではなく、現mainの学習内容・履歴・親隔離を壊さず既存試作を再評価可能にすること。

PR11は旧main86514ed基点で、main60d1a94には江戸ページ、理科内のメダカ/顕微鏡、recallを含む履歴・復習と対応検証が追加されている。実際の差分で以下の接点を確認した。

- scripts/cloud/serve.py：mainはedo-review.htmlを許可、PR11はcontent-review.htmlを追加。片方を選ぶ解消はもう片方のプレビュー入口を失うため、両方を限定許可する必要がある。
- scripts/check_all.sh：mainはedo/medaka/microscopeの3suiteを追加、PR11は教材確認/案内/読込保全/試し解きの4suiteを追加。全て保持し、現候補の必須suite集合を作る。
- tests/parent_mode.py：mainには理科recall回答操作、PR11にはcontent-reviewだけの固定hash例外と全学習HTML防御がある。両方を保持する。江戸も学習入口として親隔離を要求し、contentを理由に除外しない。
- READMEの両系列の説明も併存させ、試作・未採用・未公開の状態を明確にする。

限定追従は必要であり、既存PR11内で進めることを推奨する。PR10の6d01386は別の復習改善として前回完了済みで、今回の対象に取り込まない。PR11の教材確認/試し解きを再実装せず、新規製品PR・同時実装枠も増やさない。

## 受入条件と保持境界

1. 現main60d1a94を既存PR11の履歴を保つtopic候補へ取り込み、main自身へpush/mergeしない。対応する現mainの学習HTML（江戸を含む）、共通assets、recall履歴/採点/復習、問題ID・保存キー・履歴形式・親runtime・通知境界は原則バイト一致で保持する。競合解消以外の製品仕様変更は不要。
2. PR11のcontent-review.html、合成fixtures、content専用tests/仕様をee51e68から保持する。原本/転記/問題案比較、未解決画像拒否、編集/再入力での確認失効、後着JSON読込保全、確認済み合成text/choiceの試し解きG01〜G13/S01〜S13とmemory-only/終了消去の契約を変えない。確認室が新しいrecall保存形式を読んだり書いたりしてはならない。
3. 限定プレビューは江戸とcontentの両入口を許可し、元のloopback/CSP/no-store/HEAD拒否・API遮断を維持する。未知ファイルの一般許可に広げない。
4. 必須check_allはmainの全suiteとPR11の4content suiteの和集合を保持し、同名suite重複を作らない。現在の差分なら計29suiteを見込むが、最終スクリプトを数え実行結果で報告する。古い26suite証拠を新候補の合格へ読み替えない。
5. 親モードの全学習HTMLガード、理科recallの回答操作、contentのみの固定hash/memory-only例外を保持。contentを変えないなら既存固定hashを維持する。隔離コピーの生成器再実行、未知HTML/改変content拒否、江戸を含む新しい学習入口の親境界を確認する。
6. 実装者とは別のQAが固定clean HEADで全必須suiteを実行し、768×1024のfresh contextで教材確認→明示確認→試し解き→終了を確認。試行回答・結果を案JSON/学習履歴へ混ぜず、案・確認状態が保たれることを確認する。現mainの新学習機能/親モード/履歴回帰はそのrequired testsを維持して検証する。試験の通信はmock/合成に限定し、観測範囲と未検証事項を区別する。
7. 最終PR差分をmain60d1a94相対でも読み、今回の追従によってmain既存の新ページ・教材・recall・履歴を巻き戻していないことを確認する。PR10独自の改善を今回採用したと報告しない。

## 対象外と終了条件

新しい教材や機能、実教材/画像/回答の接続、OCR/LLM、D02保存先決定、本人試用・学習効果の推定、実機Safari/iPad保証は対象外。新CEO回答を受領しておらず、D04方向性採用を製品採用/公開承認へ広げない。

本番merge/公開/deploy、実メール/Chat/Slack、課金、Secrets/権限/共有/設定/旧自動更新変更は禁止。製品待ち10/11/12上限3を維持し、既存PR11のdraft更新だけで保存する。独立QA合格後はCEO判断待ちとして仕様・候補commit・テスト証拠・次の一手を統括が正本へ保存しleaseを解除する。同原因2試行または時間枠で未解決なら具体的な互換性障害と未検証範囲を保存し、未完を合格扱いしない。

今回PdMが実施したのは公開仕様/台帳/指定git差分の静的照合のみ。候補の実行可能性・テスト成功・最終統合を実測した報告ではない。
