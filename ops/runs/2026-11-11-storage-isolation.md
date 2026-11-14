# REV-COMPAT-FIX: 合成試作の保存隔離

run `cycle-20261110T1503Z`。2026-11-11 00:03 JST開始。
provider=cloud/running/connected/最新観測を確認し、正本
`e8bb552ead5e1b2da15e490d3eb754c3ce279879`の4文書を同じcommitから取得。
通常pushでleaseを取得してから分担した。

## 対象と範囲

前回の `REV-COMPAT-FIX` を継続。PdM `pdm_isolation_scope` がPR #19と#20の
教材版・理科・共通設定への影響をコードから確認し、PrMが既存draftの修正範囲を確定した。
製品基点はPR #20 `c5c6c15c4968ee3d04f8a43f273f12bbb3b9b81e`。
#19は `e7c727fdc2788969781ad2e34048d7d1d0b488f2`。製品採用やマージの承認ではない。

実装は独立checkout `/workspace/yuika-review-storage-isolation-20261111` で
Engineer `engineer_isolation_fix` が担当。Reviewer/QAは別の `qa_isolation_fix`。
同時実装1件、子はこの3名だけ。子はpushせず統括が実行権と対象HEADを確認する。

仕様H1〜H7は [履歴互換性契約](../../docs/product/review-history-contract.md) を基準とし、
PR19/20について以下を具体化した。

- 社会3単元に理科詳細履歴とindexの前回単元設定を加え、4ページを対象にする。
- `questionVersion`は既知の任意event項目として保持。版なし回答へ後付けしない。
- 理科はschemaVersion 2、数値response/inputRaw、events/legacy、重複排除後の上限を維持。
  社会schemaVersion 1へ変換しない。
- 理科の旧集計からの自動コピーは停止し、明示取込だけとする。旧詳細KEYと旧集計KEYは書換えない。
- 既存の採点・選定・再確認間隔・問題版archive・通知workflowは修正範囲に含めない。

## 環境の利用

既存クラウドvenvを、このcheckoutの無視対象 `.venv/bin` から参照して有効化した。
`source scripts/cloud/activate.sh` 後のPythonは既存venvで、Playwright importを確認。
依存インストール・setup・公開環境設定変更はない。自動snapshot引き継ぎの成功とは扱わない。

## 完了時の証拠

最終製品commit **`408805b06092b9eec5971426a8a1c2cb45194620`** を既存
[draft PR #20](https://github.com/naoyanakajima-cyber/yuika-study/pull/20)へ通常pushした。
統括がremote leaseの所有者/期限、対象PRの旧HEAD、候補のclean状態を確認した後に統合。
GitHub readbackでもHEAD一致・open/draft・未マージを確認した。

- 独立QA `qa_isolation_fix` が最終HEADで `source scripts/cloud/activate.sh` 後に
  `bash scripts/check_all.sh` を実行。**全17suite終了0、106秒**。Worker 9/9、bootstrap 13/13。
- 768×1024 Chromium、社会3単元・理科で同一originの旧PR10→試作→旧PR10→試作を検証。
  旧raw・旧設定・他単元はbyte一致、試作の回答も再読込後に保持。
- 実ダウンロードJSONを空の試作へ実アップロードし、questionVersionを含む完全復元と再取込の重複なし。
  未知形式/field/版の拒否、拒否原文の実ダウンロード、cross-tabの有効/破損更新を確認。
- 新規suiteは空文字を含む破損raw保護、ID衝突、未知mode、容量不足後再試行も確認。
- 独立probeのPOST試行/到達・外部request・pageerrorは全て0。通知suiteは模擬APIのみ。
  既存assert・CSP・TLS検証を維持。問題版archiveは不変。
- Engineerのfocused初回にはテスト側native関数戻り値によるIllegal invocationがあり、void wrapperへ訂正。
  最終HEADの独立17suiteとprobeは初回成功。生成後もHEAD不変・clean、`git diff --check`成功。

[独立QA報告](../evidence/2026-11-11-storage-isolation/QA.md)、
[全suiteログ](../evidence/2026-11-11-storage-isolation/check_all.log)、
[独立probe](../evidence/2026-11-11-storage-isolation/probe.py)、
[結果](../evidence/2026-11-11-storage-isolation/probe-result.json)を合成証拠としてcommit保存。
probeはこのrunのcheckout/artifactパスを固定している。別の環境で再実行する際は対象SHAを取得し、
ROOT/OUTをそのクラウド内checkout/出力先へ合わせる。probeは製品コードを書き換えない。
QA報告SHA256: `d2924d48c673e6c5e1137419be6e42912c5c635d14bac5bdf2aded9cdce09de7`。
合成画面PNGはクラウド内 `/workspace/work/isolation-qa-20261111/onin-prototype-home.png`。
統括も表示を確認。iPad実機Safari・CEO本人の操作・学習効果の検証は未実施。

## 新たに確認した既存制約と次の仕事

理科は起動時localStorage読取拒否でblockedとなった後、アクセスが戻ってもpersist=false。
基点 `c5c6c15` と最終HEADの両方で独立再現し、新規回帰ではないことを確認。
[比較結果](../evidence/2026-11-11-storage-isolation/access-recovery-result.json)と
[再現probe](../evidence/2026-11-11-storage-isolation/access_recovery_probe.py)を保存した。
データ上書きはなく、容量不足後の再試行とは別の制約。`REV-STORAGE-RECOVERY`で既存PRの
小さな修正として次回PdM/PrMが受入条件を確定する。今回追加実装しない。

製品待ち#10/#11/#12の3件に加えて未採用の追加draft #14〜#20が7件ある。
#20の修正を新たな採用や追加待ち枠とは扱わず、`REV-COMPAT-FIX`はQA済み・採用整理待ちとする。
`PR-RECONCILIATION-01`で全体の超過を明示し、新規製品PR作成を停止する。
CEOには朝夕チェックで既存試作品と追加系列の採用整理を提示し、返答前のマージや公開は行わない。
旧混在rawの旧版復帰は別の未解決課題であり、予防的な隔離で解決済みとはしない。
新規製品PRを作らず、既存PRの修正として扱う。後続PRへの自動反映も仮定しない。
私的資料・実回答・実通知・マージ・公開・課金・Secrets/権限変更は行わない。
