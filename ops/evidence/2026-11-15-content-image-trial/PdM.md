# CONTENT-MVP：読める合成図形画像の確認・試し解き

PdM `pdm_content_trial_delivery`、2026-11-15。正本07859feの前回提案とlease取得20348baの台帳、製品基点d75a5469fbf1e8c5011a6307308546e5ec669cebのsourceAsset/画像描画を読取り照合。cycle-20261115T100218Zの既存PR11内で進める最小仕様を提案する。PdMは製品・ops編集、試験、pushを行っていない。

## 目的・対象

保護者役が画像の根拠を見て転記を直し、問題内容を明示確認して、保存しない試し解きへ進める成功経路を1例作る。実児童の到達度測定ではない。追加は手作り説明SVG1枚と対応するdraft問題1問・選択入口・信頼済みasset対応・合成回帰検証。画像生成/OCRツールは使わず、コードで描く教材図fixtureで成立させる。

## 具体的な教材例

「三角形の辺」を使う。原本は600×320程度のSVGで、白背景、濃色の閉じた三角形を大きく描き、各辺に1/2/3の小さな番号、下部に読み取れる大きさの「三角形の辺は3本です。」を置く。見出しと注記に「合成の教材図・OCRは実行していません」と明記し、title/descを持たせる。外部image/font/script/リンクは埋め込まない。三角形の辺の数は原本の線から数えて照合でき、教材上の解釈も単純である。

新sourceは例としてkind=image、sourceId=synthetic-triangle-source、locator=synthetic-triangle-source.svg。新package/question IDはdraft-synthetic-triangle-package / draft-synthetic-triangle-sides-001。unitは既存schemaに収まる独立draft用識別子にする。実装時の出典領域は実SVGの三角形と説明文を包むpage:1;region:x,y,w,hと一致させる。

初期案は確認待ちの転記「三角形の辺は［確認待ち］本です。」と、quote=［確認待ち］、candidates=[3,4]（値は文字列）、resolution=nullを持つ。これは読取不能な実原本でもOCR結果でもなく、照合操作を検証するため意図的に作った合成の転記案と画面で説明する。quote/candidatesは照合後も消さない。

問題は短答で「この三角形の辺は何本ですか？ 数字で答えてください。」、answer=3（文字列）、aliases/readings/optionsは空配列、説明「三角形は3本の辺で囲まれた図形です。」、ヒント「まっすぐな線を1本ずつ数えよう。」。generatedFieldsにはprompt/explanation/hintを付け、原本の文と問題案の説明を区別する。status=draft、confirmedRevision=nullから始める。正答候補は用意した案であり、resolutionや確認を自動確定しない。

## 最小受入

1. 新しい「画像・読める図形の例」入口は既存サンプル同様の未保存破棄確認を通し、別の原本として正しいSVGを表示する。旧画像入口・旧原本・旧fixtureはそのまま保持する。
2. 初期は未解決1件のため確認/試し解き開始不可。テスターが原本を見て転記を「三角形の辺は3本です。」へ直し、resolutionへ3を入力し、問題案を照合して明示確認する。各編集でrevision増加・全確認失効、明示確認後だけ開始可。転記とresolutionは利用者の照合であり、機械が意味一致を保証したとは言わない。
3. 1問の開始→回答3→登録答えとの一致表示→終了を実DOMで確認し、回答4で不一致になることも合成QAで確認。終了後は案・確認・unsavedを保持し試行回答/結果を消去する。試行中は原本/編集領域を隠し、案編集/入出力を遮断する既存契約を保つ。
4. 未確認JSONと確認済みJSONの保存・再入力でschemaVersion=1を維持し、再入力時は全問draftへ戻る。試行回答/結果・assetコードを案JSONへ追加せず、確認後の再編集で再び開始拒否になる。
5. ASSETSの単一image参照を、既知sourceのkind/sourceId/locatorに対応した信頼済み同梱asset選択へ限定変更する。JSON由来SVG/URLや任意locatorを描画しない。新旧画像切替とJSON再入力で原本取り違えがないことを検証。unknownsourceは引き続き拒否し、旧判読不明画像を成功扱いしない。
6. 768×1024 fresh contextで文字・図・出典領域を視認し、keyboard/focusと状態案内を確認。新成功経路に加えて未解決/未確認/編集後/unknownsourceの負例、旧text/choice・非同期取込保全・試行消去を検証する。固定clean HEADの必須全suiteへ新回帰を含め、独立QAが実行する。
7. 現mainの学習HTML/ID/採点/recall履歴・保存キー・親runtimeは不変。CSPを変えず、storage/history/cookie/外部通信・通知へ試行情報を書かない。変更HTMLの固定hash2箇所を整合し、未知HTML/改変content拒否を保った独立memory-onlyレビュー後に受入する。

## 対象外・リスク・判断

私的教材写真/実回答/メールDrive、外部画像/OCR/LLM、D02実接続・保存先、教材本体登録、schema/既存学習記録変更、新しい採点規則・自動照合は対象外。新CEO回答や採用/公開承認を推測しない。製品待ち3枠を維持し新規PRなし、今回の成果は既存PR11のdraft候補まで。

主なリスクは、単一ASSETS.imageのまま新JSONだけ増やして旧原本を誤表示すること、合成確認待ちを実OCR結果と誤認させること、fixtureが最初からconfirmedになること。明示asset対応・注記・初期draft/未解決と負例QAで防ぐ。実機Safari/iPad・本人試用・学習効果をこの合成検証で保証しない。

PrMがこの範囲を採択した後、Engineer→独立QAの順で進める。時間不足/同原因2試行で未解決なら未完条件を具体的に保存し、成功扱いしない。今回のPdM成果は仕様提案のみ。
