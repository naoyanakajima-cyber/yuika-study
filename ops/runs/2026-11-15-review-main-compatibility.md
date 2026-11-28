# 2026-11-15 外部main更新と既存復習PRの互換性追従

状態：既存draft PR10へ固定候補6d01386を保存、独立QA完了、CEO判断待ち。最終保存時刻 2026-11-15T08:29:45.865542+00:00。

運用source b35eef2、lease78358b2を通常push後にPdM/QAを起動。外部でPR27→28→29がmergedとなり、観測mainは60d1a946cc02ed8acea54c0d7af7d6451fcc30ec。各merge treeは対応PRhead treeと一致し、前回PR27修正を含む。外部行為を本運用のCEO承認や自分が行ったmergeとして記録しない。新CEO返答の実読0。

メダカ17問・江戸22問と2段階想起により、自力で思い出せたかを最終正誤と区別する。画像/テキスト入力機能の完成やテーマ全画面拡張ではない。独立QAは現main25suiteを初回25/25成功・308秒、別probe4fresh contextで中断未保存/最終1event/assistedの復習対象維持/元raw不変/親保存隔離を確認。以前の作者報告と今回の実行を区別する。

Pages/Workersの現在main APIcheckはsuccess。公開画面の取得・本人試用・実機Safari/iPadは未確認。過去PR27headのWorkers failureは別の履歴として保持し、同一障害の解消と断定しない。今回merge/公開/手動deploy/実送信/課金/Secrets/権限/自動化変更なし。

PdMが最初に照合のみを提案し、PrMはmain QA成功かつ18分以上残る場合の既存PR10候補作成へ範囲を更新した。08:15:55 UTCにmain QA完了、残り25分以上を確認。Engineerは73fe2eeを保持する独立checkoutでmain60dとのtopic統合と必要な生成整合を進める。理科生成後に江戸も再生成し、両系列の必須試験を維持する。候補は実装者とは別のQAを通るまで既存PRへpushしない。時間不足時は未完checkpointと残件を保存する。

仕様はdocs/product/daily-count-spec.md末尾、担当/根拠はops/evidence/2026-11-15-review-main-compatibility/を参照。実装は同時1件、担当はPdM pdm_theme_compatibility、Engineer engineer_theme_compatibility、独立QA qa_theme_compatibility、統括root。製品待ち10/11/12の3枠と既存draft22を維持し、新規製品PRは作らない。

## 最終成果

PR10: https://github.com/naoyanakajima-cyber/yuika-study/pull/10

候補6d01386dba0bb3cdafa7e8f431a6a17bc81e913fは旧PR10 73fe2eeとmain60d1a94を親に持つtopic統合。既存の理由付きおすすめ（応仁/鎌倉）と6画面の日次実問数を、新教材・2段階回答の読み取り判定を保持して提供する。実験器具10設定なら表示8/実8、メダカ/江戸の選択肢正解は保存正解でも苦手復習に残る。理科後に江戸を再生成した。新しい教材取り込みやテーマ拡張は行っていない。

Engineerの重点4suite・追加recall件数回帰と生成一致は独立QAと区別。独立qa_theme_compatibilityは固定clean候補で全29/29初回成功（349秒、08:26:18 UTC完了）、限定7fresh contextで器具/有効単元/未知単元と通常/親のrecall履歴を確認。全6アプリの問題/ID/キーを現mainと照合。詳細・全suite表はevidenceのQA-candidate.md、実ログ・合成画像・SHA256SUMSへ保存。再試行で成功へ寄せたテストはない。Engineerの補助静的スクリプト2件の誤りはEngineer.mdに区別して記録。

統括は有効lease、ops e1ac1da、PR10旧73fe、main60d、candidate cleanを確認し通常push。PR10 HEAD6d01386/open/draft/unmergedと本文をreadback。新規PR0、既存製品待ち10/11/12の3件、別既存draft22を維持。既存PR10へのattachを呼び出した。

## 外部検証と限界

同candidate HEADのWorkers Builds: yuika-studyは08:27:48 UTCにfailure。公開GitHub check https://github.com/naoyanakajima-cyber/yuika-study/runs/132752305706 。checkから原因詳細は取得できず、旧headの失敗と同一原因とは断定しない。combined status pending/0件はcheck-runsのfailureとは別フィールド。外部checkを再実行・手動deployせず、設定変更もしない。main60dの別Workers/Pages successをcandidate成功へ転用しない。公開ページは未確認。

検証済venvを手動再利用し、requirements一致と正規activateを確認。自動snapshot成功とは扱わない。新規実回答/写真/メール/Drive・実送信なし。Chromium合成確認のみで、本人試用・Safari/iPad実機・学習効果・全教材の事実再校閲・他PR11/12との統合・多タブ同時確定は未検証。新recall JSONの旧版逆互換を保証しない。1/3/7日間隔は仮案。

## 次の一手

CONTENT-MVPの既存PR11 ee51e68を最新mainと固定比較し、確認→保存しない試し解きの親隔離・新ページとの互換性をPdM/PrMで限定して既存PR内で進める。THEME-MVPも後続で共有runtime/新テストの保持を照合し、全画面拡張はしない。新差分がなければ同じQAや環境調査を反復しない。

CEO判断はこの運用を設定した元チャットへチケットIDを添えて返信し、実読担当が台帳へ反映するまでworker伝達済みと扱わない。今回新返答の実読0。通常報告と外部check失敗は朝夕CEOチェックへ集約。終了時lease解除、毎時の個別通知なし。

最終保存検査で、証拠へ複製したraw diffの空context行がtrailing whitespaceとして検出された。製品テスト失敗ではない。重複するdiff本文2件のみ共有証拠から除き、再生成用commit/commandとSHAをomitted-source-diffs.jsonへ保存、manifestを更新した。原本/tmpと製品commitは不変。修正後のstaged検査は2回目を実行。
