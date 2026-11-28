# 保存しない合成教材試し解き：独立QA

Reviewer `qa_content_trial_delivery`、実装者 `engineer_content_trial_delivery` とは別担当。対象初回候補8e2111b4e9c535c4632976a6f384992e839d1329、基点62f34de238e9d1d62c796aac3a4b43418043d17f。cloudの独立checkoutを読み取り、製品/ops編集・push・設定/権限変更・実通知なし。既存venvを手動有効化し、自動snapshot成功とは扱わない。

## 初回候補の観測

固定clean HEADでcheck_allを実行中。独立probe65ケースはPASS。短答26例（G01〜G12とUTF-16/型/内部空白等境界）、choice8例（G13）、開始拒否12例、状態/副作用19ケースを実測。G/S表の全IDを横断しているが、追加実UI導線観測で下記の不足があるため初回候補を受入済みとはしない。

読み込みは実file inputと同梱合成JSON、確認/回答/ヒント/採点/次へ/終了は実DOMで操作。型異常、古いセッション/問題/epoch、案内容や確認の不整合、表示DOMの再構築は合成fault injectionを併用。文字列はNFKC+trimのみ、choiceは整数identityのみで、生/正規化後の200上限を検査した。初期draft/一部確認/旧版確認/不正source・shape/未解決画像/正規化過長候補/外部confirmed再入力/取込待ちを開始拒否した。

案・revision・確認・unsaved不変、採点前の正答/解説と編集領域のAX除外、キーボード/見出しfocus、ヒント、再採点/前問イベント拒否、JSON非混入、終了/再開始、編集で全確認失効を検証。768×1024の回答中・採点後画像を目視した。probe範囲で監視保存/history/cookie/IndexedDB/Cache/SW操作、非許可要求、POST、pageerror、console出力各0。window.name空。実reloadのbeforeunload取消は同一文書を保持、了承reloadは新文書trial/proposal=null。persisted pageshowは合成イベントで消去を確認し、実ブラウザーのBFCache成立を証明したとは扱わない。

初回probeは採点26例後のハーネスFile.text置換evaluateが関数を返し、Playwrightが呼び出して未解決Promise待ちとなった。プロセスを停止しvoid0終端に修正、2回目で65ケース完走。製品不具合による失敗や無診断3回目として扱わない。必須suite/staticとは独立した試行履歴である。

static境界は初回PASS。既存6学習HTML、CSP、validateShape/issues、同梱SAMPLES/ASSETSは基点と一致。固定hash2箇所は値だけ整合し、防御を緩和していない。git archive隔離コピーで改変CONTENTを生成器が書込み前拒否し、親preflightが未知HTML/改変CONTENTを拒否した。意図した負例非0は防御成功。

## QA差戻し：正規化過長候補の修正導線

PrMからの懸念を独立した実UIで検証。合成text案の別表記欄に㍍×51を入力し、個別確認すると、開始ボタンはdisabled・原因は「別表記を変換後も200文字以内」と表示される。しかしその原因から修正欄へ移動する操作がなく、既存「次の作業へ」はJSON保存欄へ移動する。`startTrial()`の直接関数呼出でfocusできることは、利用者の画面操作から移動できる証拠にはならない。

`start-guidance-result.json` / `normalized-candidate-guidance.png` に対象HEADと実測を保存。既存G/S開始条件の「原因と該当欄への移動を示す」に対して修正が必要。初回全suite完了まで同じ候補を維持し、その後最小修正・新候補固定・独立再検証とする。

## 限界

合成text/choiceのみ。実児童の回答/理解度、私的教材、OCR、実画像成功、既存教材登録、公開、実機iPad/Safari/WebKit、実BFCache成立は未検証。現行試行内容はメモリのみで、学習記録/実通信に接続しない。全必須suiteには公開CDN読取り・模擬通知があるため、全体外部要求0とは言わない。
