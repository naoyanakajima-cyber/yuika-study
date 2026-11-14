# 保存しない合成教材試し解き：独立QA

Reviewer `qa_content_trial_delivery`、実装者 `engineer_content_trial_delivery` とは別担当。対象初回候補8e2111b4e9c535c4632976a6f384992e839d1329、基点62f34de238e9d1d62c796aac3a4b43418043d17f。cloudの独立checkoutを読み取り、製品/ops編集・push・設定/権限変更・実通知なし。既存venvを手動有効化し、自動snapshot成功とは扱わない。

## 初回候補の観測

固定clean HEADでcheck_all初回26/26・exit0・296秒。検証終了後も同HEAD/cleanを23:23:06Zに確認。独立probe65ケースはPASS。短答26例（G01〜G12とUTF-16/型/内部空白等境界）、choice8例（G13）、開始拒否12例、状態/副作用19ケースを実測。G/S表の全IDを横断しているが、追加実UI導線観測で下記の不足があるため初回候補を受入済みとはしない。

読み込みは実file inputと同梱合成JSON、確認/回答/ヒント/採点/次へ/終了は実DOMで操作。型異常、古いセッション/問題/epoch、案内容や確認の不整合、表示DOMの再構築は合成fault injectionを併用。文字列はNFKC+trimのみ、choiceは整数identityのみで、生/正規化後の200上限を検査した。初期draft/一部確認/旧版確認/不正source・shape/未解決画像/正規化過長候補/外部confirmed再入力/取込待ちを開始拒否した。

案・revision・確認・unsaved不変、採点前の正答/解説と編集領域のAX除外、キーボード/見出しfocus、ヒント、再採点/前問イベント拒否、JSON非混入、終了/再開始、編集で全確認失効を検証。768×1024の回答中・採点後画像を目視した。probe範囲で監視保存/history/cookie/IndexedDB/Cache/SW操作、非許可要求、POST、pageerror、console出力各0。window.name空。実reloadのbeforeunload取消は同一文書を保持、了承reloadは新文書trial/proposal=null。persisted pageshowは合成イベントで消去を確認し、実ブラウザーのBFCache成立を証明したとは扱わない。

初回probeは採点26例後のハーネスFile.text置換evaluateが関数を返し、Playwrightが呼び出して未解決Promise待ちとなった。プロセスを停止しvoid0終端に修正、2回目で65ケース完走。製品不具合による失敗や無診断3回目として扱わない。必須suite/staticとは独立した試行履歴である。

static境界は初回PASS。既存6学習HTML、CSP、validateShape/issues、同梱SAMPLES/ASSETSは基点と一致。固定hash2箇所は値だけ整合し、防御を緩和していない。git archive隔離コピーで改変CONTENTを生成器が書込み前拒否し、親preflightが未知HTML/改変CONTENTを拒否した。意図した負例非0は防御成功。

## QA差戻し：正規化過長候補の修正導線

PrMからの懸念を独立した実UIで検証。合成text案の別表記欄に㍍×51を入力し、個別確認すると、開始ボタンはdisabled・原因は「別表記を変換後も200文字以内」と表示される。しかしその原因から修正欄へ移動する操作がなく、既存「次の作業へ」はJSON保存欄へ移動する。`startTrial()`の直接関数呼出でfocusできることは、利用者の画面操作から移動できる証拠にはならない。

`start-guidance-result.json` / `normalized-candidate-guidance.png` に対象HEADと実測を保存。既存G/S開始条件の「原因と該当欄への移動を示す」に対して修正が必要。初回全suite完了まで同じ候補を維持し、その後最小修正・新候補固定・独立再検証とする。

## 限界

合成text/choiceのみ。実児童の回答/理解度、私的教材、OCR、実画像成功、既存教材登録、公開、実機iPad/Safari/WebKit、実BFCache成立は未検証。現行試行内容はメモリのみで、学習記録/実通信に接続しない。全必須suiteには公開CDN読取り・模擬通知があるため、全体外部要求0とは言わない。


## 最終修正候補の再検証

導線だけを修正した候補 **ee51e68d7e1eeb21bd0e959ec58166a869947d0a** をclean/freeze確認して再検証。初回8e2111bの全証拠・harness診断・差戻しは `attempt1/` に保全し、root直下は最終候補の証拠とする。最終候補に対する独立65ケースprobe、static境界、修正導線probeはそれぞれ初回PASS。初回候補のハーネス原因を無診断で3回試したものではなく、修正commitに対する検証である。

`#trial-repair` の実Enter操作により、正答・別表記・読みの各正規化後過長条件から該当入力へ移動した。別表記/読みの祖先detailsを閉じた状態でも展開され、入力が可視かつfocusedとなる。未確認時はconfirm-0へ移動し、正常全確認時はrepairが非表示、試行中はeditor全体が非表示。初回の導線blockingは解消。

最終probeは採点後の回答欄value保持も追加assertして通過。最終候補の全必須26suiteは初回で26/26・exit 0・256秒。完了後にも同HEADとcleanを確認した。

### 画像証拠の範囲

連続操作直後の `graded-768x1024.png` はblankとなり、視覚合格の根拠には採用しない。DOM上は試行がGで、回答欄valueと結果・focusのassertは成功していた。スクロール位置または描画/キャプチャのタイミングの可能性はあるが、原因は特定していない。

同じ最終HEADの新規contextで、実サンプル選択→個別確認→開始→「こおり」入力→採点を独立して実行。DOMのtrial.answer/textarea.valueがともに「こおり」、phase G/match trueを観測した。描画待ち後の `graded-visual-768x1024.png` では入力値・一致結果・正答/読み・解説・終了操作を目視できた。`answering-768x1024.png` と `normalized-candidate-guidance.png` も目視済み。この範囲でUIを確認したもので、全描画タイミングに問題がないという保証ではない。元のblank画像を削除していない。

## 最終判定

2026-11-14T23:29:10.778434+00:00 に固定最終HEAD/cleanを再確認。独立QAは **draft PR・CEO判断待ちへ進める範囲でPASS**。blocking残件なし。本番マージ/公開の承認ではない。G01〜G13採点、S01〜S13状態契約（S04は空/過長等の採点拒否とその後の継続操作で検証）、保存非書込、既存import guard、採点前非表示とfocus、DOM再構築/古イベント拒否、guard負例を実施した。詳しい結果と26suite一覧は `final-result.json`、最終候補証拠は直下、初回候補とハーネス診断は `attempt1/`。全証拠ハッシュは `SHA256SUMS`。次は統括による実行権再確認、PR11更新、台帳への仕様/担当/テスト結果保存・lease解除。
