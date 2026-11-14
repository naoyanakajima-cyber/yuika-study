# PR26 外部マージの照合（2026-11-12）

## 成果と受入範囲
PR26の教科別弱点対策・横スクロール改善・不正教科URLの46問fallbackを、既存の検証済み成果としてmainとの同一性を照合する。新しい製品実装は行わない。PdMの受入条件をPrM rootが確認し、この範囲を採用した。個人資料・実回答は使用しない。

正本4文書を同じcommit e8a4012cbd25efc4c120a0cb3a280b430e512c1cから確認。クラウド実行を確認し、cycle-20261112T130615Zのleaseを通常pushで取得した。PdM pdm_merge26_reconcile、独立Reviewer qa_merge26_reconcileを起動。製品実装がないためEngineerは起動しない。

## 観測した外部変更
- [PR26](https://github.com/naoyanakajima-cyber/yuika-study/pull/26)は2026-11-12T13:01:23Zにmerged。最終HEAD acd169882b626ef255ba68cd73c995024c30e515、マージcommitおよび観測mainは86514eda054a5a2e09204df3a0668e40624c16de。
- 旧draft表記は更新するが、PR本文の「所有者承認」は本運用の新CEO返答として取り込まない。adopted=falseは本運用で新承認未取り込みを示し、mergedの事実と区別する。今回のマージ/公開実行は0。
- 両commitのtreeはfc44857441e0f2344e488d141c5c4fa47065a0c6で一致し、ファイル差分なし。検証HEADと前回提出待ち修正5b77225はmainの祖先。元df791c0の変更は5b77225として含まれる。
- [Pages run](https://github.com/naoyanakajima-cyber/yuika-study/actions/runs/43223305924)のAPIはhead86514ed・completed/success、更新時刻13:02:06Z。公開画面の実表示、本人試用、実機Safariは未確認。外部deploy観測を今回のdeploy実施・追加権限と扱わない。

## 検証の扱い
独立22suite成功・URL8ケース成功は前回acd1698の証拠を維持。今回アプリ/ブラウザーテスト0、依存導入0、手動setup0。生成tree同一のため全suiteを繰り返さない。追加設定probeの終了後復元は未検証、通常parent_modeの終了検証成功とは区別。元のPR25初回失敗の直接原因未確定、Chromium限定も維持。

## 台帳と次の仕事
PR26はmergedへ、提出待ち修正・SUBJECT-URL-01・PARENT-MODE-QA-01をmain包含観測へ更新する。過去run/証拠は変更しない。製品ceo_wait #10/#11/#12の3件と追加open draft #22を明示。#26のmergeで新規製品PRの枠が空いたとは扱わない。旧#4〜#8と運用#9/#13は別。

今後は苦手復習の合成試用から具体的な修正依頼・再現不具合・新差分が出た場合に対応。PR26はclosedなので同じPRへ追記せず、提出先と待ち枠を照合する。既存の教材追加合成フローが次順位、テーマ低優先。D02の実データ保存/接続は別判断、方向性採用を再要求しない。独立して進められる仕事がない場合は終了する。

## 運用
新しいCEO判断取り込み0、新規PR0。既存運用draft PR9へ文書/台帳を保存しlease解除する。既存attachの無応答は成功未確認のまま、状況変化なく再試行しない。旧自動化再開・実通知・課金・Secrets/権限/共有変更・本番マージ/公開操作なし。通常成果は朝夕チェック用に保存し、外部通知なし。

独立Reviewer qa_merge26_reconcileは祖先/tree/差分と保存QAを照合し、Pages3ジョブもAPIで成功確認。報告草案に事実誤認なし。証拠: ops/evidence/2026-11-12-pr26-merge/QA.md。

最終文書確認: qa_merge26_reconcile が台帳/報告の事実一致、コピー2点の原本byte一致・hash2/2一致、過去run未変更を確認。最終保存・lease解除記録: 2026-11-12T13:10:04.212544+00:00。
