# 2026-11-15 教材確認試作の現main互換性

状態：CONTENT-MVP既存PR11の限定候補を実装中、独立QA未完。

正本c1fa98cの4文書/台帳を確認し、クラウドrunning/connectedを確認。lease214df00を通常push後、PdM→PrM採択→Engineerを起動した。QA担当は別エージェントで仕様レビューと検証準備、候補固定後に実行する。担当はpdm_content_trial_delivery / engineer_content_trial_delivery / qa_content_trial_delivery、統括root。

旧PR11 ee51e68とmain60d1a94の4接点（README、限定serve、suite登録、親テスト）を両保持し、現学習画面と同じ候補で合成教材案の確認・保存しない試し解きを試せる状態へ追従する。確認室HTML/fixture/hashを保持し、mainの教材/recall履歴/親runtimeを巻き戻さない。新機能や私的教材接続、PR10/12の一括取り込みは対象外。

候補実装は独立checkout /workspace/yuika-content-main-compat-20261115。既存PR11を保存先に維持し、製品待ち10/11/12上限3、新PRなし。新CEO返答の実読0、本番merge/公開/実通知/課金/Secrets/アクセス変更なし。詳細scopeはdocs/product/content-spec.md末尾とops/evidence/2026-11-15-content-main-compatibility/PdM.md。
