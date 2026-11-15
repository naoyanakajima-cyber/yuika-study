# 2026-11-15 教材確認試作の現main互換性

状態：既存draft PR11へ固定候補d75a546を保存、独立QA合格、CEO判断待ち。最終保存時刻 2026-11-15T09:19:00.010826+00:00。

## 学習上の成果

[PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11) の合成教材確認→保存しない試し解きを、江戸・メダカ・顕微鏡とrecall履歴が入った現mainと同じ候補環境で使える状態へ追従した。確認室HTML/原本fixture/案schema/固定hashは旧PR11 ee51e68から維持し、mainの問題・学習/ホームHTML7件・assets・親runtime・採点/履歴意味を巻き戻していない。新しい実教材取り込みや画像成功経路の実装ではない。

正本source c1fa98c、クラウドrunning/connected確認、lease214df00通常push後にPdMを実起動。PrMが限定scopeを採択し、Engineerが独立checkoutでee51e68+main60d1a94をtopic統合。唯一のmerge競合はserve許可一覧で、江戸/content両方を保持した。親testに江戸必須存在、preview regressionに江戸GET/CSP/no-store/HEAD405を追加。全suiteを和集合29件に保持。PR10/12の独自改善は取り込んでいない。

## 実行と独立レビュー

担当PdM pdm_content_trial_delivery、Engineer engineer_content_trial_delivery、独立QA qa_content_trial_delivery、統括root。子3名、同時実装1件。固定候補 d75a5469fbf1e8c5011a6307308546e5ec669ceb、独立QA全29/29初回成功325秒、09:15:16 UTC前後clean/HEAD確認。全suite表/ログはevidence/QA.mdとqa/へ保存。Engineerのfocused preview/parent2suiteと静的検証は別証拠。

独立HTTP9境界（content/江戸200、未知/私的風fixture経路404、HEAD405、loopback API POST501）と、768×1024合成textの確認→試行→採点→終了→JSON出力→未回答再開始を直接検証。元案/確認/unsaved不変、案JSONに試行回答なし、監視範囲の保存操作/非許可ブラウザー要求/pageerror0。江戸の実親隔離は専用edo suiteで確認。main共有接点以外84filesと旧content12pathsのbyte一致、隔離生成器冪等、改変content書込前拒否、未知HTMLの親preflight拒否を独立確認した。

HTTP probeは本文を読まず早期closeしサーバーBrokenPipeログ1件を残した。assertは通過しブラウザー例外0、ハーネス由来と区別し元ログを保持、同probeの反復なし。旧65独立ケースは今回再実行せず、不変contentのbyte確認と現候補専用4suite/接点probeを根拠とする。全suiteのmock通知・公開JS GETと、限定probeのブラウザー非許可要求0を混同しない。

## 保存と外部check

統括がremote ops0cc0ef8の有効lease、旧PR11 ee51e68、main60d1a94とcandidate cleanを確認して通常push。直後のPR expected-state assertが不一致だったため書込を止め、2回目のPR読取とls-remoteでd75a546/open/draft/unmergedを確認後に本文を更新。初回応答fieldは保持しておらず原因断定はしない。再push/forceなし。本文の全29suite結果・HEAD・限界をreadbackし一致確認した。

同HEADの[Workers Builds: yuika-study](https://github.com/naoyanakajima-cyber/yuika-study/runs/132763996602)は09:16:20 UTCにfailure。取得checkに原因詳細なし。旧HEAD失敗との同一原因は未確認。combined status pending/0件とは別にcheck-runs failureを記録。クラウド内QA成功とは区別し、外部再実行・手動deploy・設定変更は行わない。公開画面は未確認。

初回の古いremote-tracking表示はmain限定fetch設定によるローカル参照で、ls-remote/APIで実正本c1fa98cを確認し明示refspecで更新した。正本の巻戻しはなく、4文書を実正本で読み直してからlease取得。手動の検証済venv再利用は依存hash一致/activate確認済みで、自動snapshot引継ぎ成功ではない。

## 次の改善提案と限界

[読める合成画像から試し解きまでの次回候補](../../docs/product/content-image-trial-proposal.md)をPdMが整理しPrMが保存、別QAが文書整合を確認。手作りの読める原本と信頼済みasset対応を用意し、転記照合・明示確認・試行の成功経路を示す案。未解決画像拒否や案schema/記録隔離は維持する。今回未実装で、次回最新状態とleaseを確認しPrM範囲確定後に既存PR11内で進める候補。目標②の具体的な成功経路をTHEMEの単純追従より優先する提案であり、テーマに試用を妨げる再現不具合があれば再順位付けする。

実写真/実回答/メール/Driveの取得なし。合成Chromiumのみで、本人試用・学習効果・実機Safari/iPad・実BFCacheは未確認。D04方向性を維持、新CEO返答実読0、D02実接続/保存先は未決。本番merge/公開/実メールChat/課金/Secrets・権限・共有・旧自動化変更なし。製品待ち10/11/12の3枠、新PR0、別既存draft22を維持。PR11へのattach呼出し済み。成果/外部checkは朝夕CEOチェックへ集約、lease解除して毎時個別通知なし。

CEO判断はこの運用を設定した元チャットへチケットID付きで返信し、実際に読んだ担当が台帳へ反映するまでworkerへ伝達済みとは扱わない。
