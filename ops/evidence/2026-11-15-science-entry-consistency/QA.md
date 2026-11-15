# Cycle30 Independent QA — PR27 entry consistency

独立担当 qa_theme_compatibility。Engineerと別担当で読み取りレビュー・固定HEAD実行のみを実施。元HEADは独立detached checkout、修正版は統括がfreezeしたEngineer checkoutを別担当QAが読み取り実行した（新たなQA checkout作成とは報告しない）。製品/ops編集、commit、push、merge、デプロイ、実通知、新子起動なし。実回答・教材写真・秘密情報を使用していない。

## 判定：今回の最小修正範囲は独立QA合格

元PR27 `58c3fd4ba10ecfaa249cc3c808c3e8e5fcaf5359` と最小修正版 `69f77d671b66484b501f7a0f5c292bfa96a22273` を区別。元HEADの全23suiteは264秒/exit0で06:12:34 UTC完了したが、追加独立probeで2件の実不一致を発見した。最小修正をPrMが採択し、修正固定HEADの全23suiteを新しい差分に対応して初回実行し、264秒/exit0で06:18:50 UTC完了。実行前後ともHEAD一致・working tree clean。修正版の独立4入口probeと静的範囲も成功。今回の限定修正を既存draft PR27へ保存するためのQAは合格。

## 再現・修正の確認

- 元HEAD: 未知の非空unitは生成ホーム要約total/normalCount=0/0だが、アプリはall67へfallbackし通常/日次とも5問。main86514edaでは未知unitも47/5と実5が一致。PR27導入の不一致と判定。PR10のbuild_summary差分はdailyラベルのみであり、このunit guard修正は別原因。
- 元HEAD: 20問追加後も実画面heroに「解説つき・47問」。修正版は動的「解説つき・理科全67問」で全理科と明示。
- valid顕微鏡のsummary20とglobalcounter0/67は異なる範囲を表す。実候補20・実出題5が一致し、globalcounterを単元出題数の欠陥とはしない。全理科counterは変更されていない。

| 修正版入口 | 要約total/normalCount | 実候補 | 実通常/日次 | 選択単元 |
|---|---:|---:|---:|---|
| 顕微鏡の使い方 | 20/5 | 20 | 5/5 | 顕微鏡の使い方 |
| 未指定 | 67/5 | 67 | 5/5 | all |
| 空 | 67/5 | 67 | 5/5 | all |
| 未知 | 67/5 | 67 | 5/5 | all |

全4条件で実出題IDが候補集合内、validは全問顕微鏡。全4tag「解説つき・理科全67問」、globalcounter0/67をassert。fresh合成context、Chromium768×1024、POST0・pageerror0。修正版valid/unknownの画像2枚を独立目視し、見出し・選択単元・67問tag・counter・開始操作を確認。全12画像を目視したという主張はしない。

補足probeは対象ページに同じ生成summary assetを読み込み要約関数を評価し、実通常/日次ボタンを押して問題IDを収集した。Reactホームカードのクリックはこの補足probeではなく、必須microscope suiteの既存validカード入口と、新規4条件の実ホーム要約取得/実開始が担う。main比較4条件は元HEAD時にgitオブジェクトを読み取り配信して完了し、修正版で無関係なmain試験は反復していない。

## 静的境界

元PR27→修正版は許可された4ファイルのみ27追加/3削除。build_summary.pyとprogress.jsは実在science unitだけ絞り込む同一guard。tests/microscope.pyはfresh4条件の要約/実候補/実開始/tagを追加。HTMLは「解説つき・47問」1箇所を動的tagに置換すると修正版とbyte一致し、問題オブジェクト・ID・採点・保存schema・通知・他HTMLの変更なし。元PR27そのものの全20問の科学内容監査や他PRとの統合互換性保証とは区別する。

## 実行準備と試行の区別

既存verified venvを手動再利用。自動snapshot引継ぎ成功とは扱わない。元準備のbin-only環境にlibもあると誤ったassertが1回失敗したが、runnerは有効binリンクと正規activateで開始し、suite自体は再実行していない（preparation.json）。修正版補足probe初回は直接.venv/bin/python起動でcloud activateを通さず、ブラウザ未検出により製品到達前に失敗。正規scripts/cloud/activate.shを通した同原因2回目で成功し、両logを保存。修正版全suiteは最初から正規runner経由、独立probeの準備失敗と混同しない。

元/修正版の必須suiteは公開JS GETとmock通知テストを含む。補足probeの通信遮断結果を全suiteの0通信保証へ転用しない。外部Workers失敗はGitHub側の別検証で、このQAではデプロイ調査/再実行せず、ローカル必須suite成功で外部失敗を成功扱いしない。作者の以前の23suite×3回という記載は作者報告であり、今回の独立実行数へ含めない。

## 限界・引継ぎ

空合成履歴での入口整合性が対象。保存済み設定の全組合せ、実機iPad/Safari、本人試用/学習効果、既存PR10/11/12とのmerge互換性、全科学的正確性は保証しない。既存CEO待ち3枠と外部draftPR27の分類はPrM/台帳に従い、QA成功を採用・CEO承認・main反映とみなさない。統括がleaseとremoteHEADを再確認して既存draftPR27へ統合する。

証拠ディレクトリ `/tmp/yuika-cycle30-qa/`。元/修正版stdout・実行結果・probe script/JSON・合成PNG・静的差分・失敗準備logを保存。SHA256SUMSを最終完了後に作成。基点ファイルやvenv/pycache/秘密情報を証拠に含めない。

## 最終台帳の独立読み取りレビュー

qa_theme_compatibilityが保存前の台帳/報告/証拠をe5f20f3と比較し、重大指摘なしと返答。旧139runs・12tickets・decisions/policy/authorization/decision_intake・既存findings/external entriesを保持し、run1/finding1/外部PR27を追加。owned待ち10/11/12とexternal22/27、adopted=false、実際の3担当/両HEAD23suite/初回準備失敗と再試行成功/Workers failure/未検証事項の区別は証拠と整合。31件SHA一致。PR本文と保存metadataを照合し、live GitHubを再読したとは主張しない。製品再試験・編集・pushなし。remote lease解除成功は統括による後続確認。
