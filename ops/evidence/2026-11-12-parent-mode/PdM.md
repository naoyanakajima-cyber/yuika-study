# PR24 PdM scope assessment

- Role: pdm_parent_mode_scope (actual child agent); read-only product/spec assessment, no code edits, app tests, push, private data, or external posting.
- Product source: PR24 `0d6827962b35ed24ccdbdd8f56e8dafca06f240a`, based on main `1d444f7e2c1e49912eef18c77e7ed97b3b8092f0`.
- Operations source: canonical pre-lease `e826efed6bdc4e75d5fa18660dea260435a5da40`; current lease commit `51326ee`.

## Value and scope recommendation

保護者の試用結果が子どもの誤答・再確認・今日の5問へ混ざらないことは、REV-MVP / D03 の「最優先で試せる状態と使い勝手確認」に直接役立つ。新機能を重複作成せず、既存PR24の独立QAと必要な修正に限定して進めるのを推奨する。

既存記録の日時削除は、試用隔離とは別の破壊的操作である。PR24内の実装・合成データQAは評価できるが、本運用で実データ削除を実行しない。PR本文の別タスクへの言及や既存PRのmerged表示を、新たなCEO承認として取り込まない。D02（実資料・実回答の保存先）も未決のままとする。

## Acceptance criteria for independent QA / PrM

1. 全6画面で専用入口と継続バナーを確認でき、URLパラメータ除去後も同一タブの再読み込み・単元移動で隔離が続く。
2. 回答・学習設定・弱点判定・再確認・今日の5問は専用sessionStorageに入り、子どもの既存localStorage（履歴・設定・通知保留含む）のrawが変わらない。
3. モード中の保留登録・再送・接続確認・Worker fetchを停止し、未送信を表示。通常モードの模擬通知は従来どおり。
4. 終了でモード専用記録を破棄し通常へ戻る。新規タブは通常で、ブラウザーの閉じたタブ復元の例外は明示。専用URLを本人認証とは呼ばない。
5. 保存拒否・容量不足でも子どもの保存領域へのフォールバックをせず、通常モードまで起動不能にしない。sessionStorageの初期読取/書込拒否と途中失敗を確認する。
6. 日時削除は「指定日時を含む以降」「この端末時刻」「対象全単元」「取り消せない」を件数・確認前に説明。取消・日時変更・別タブ競合で削除しない。古い日時・日時なし・未知キー・設定・通知を保持する。
7. 複数キーの削除途中に保存失敗した場合、部分削除を成功扱いしない。保全/再確認手順と実際の残存データを照合する。
8. 768×1024相当のバナー/終了/削除操作の可読性、長い学習画面でも終了が見つかることを確認する。Chromium結果をSafari/iPad実機結果としない。

## Static observations needing QA confirmation

- `scripts/parent/runtime.js` starts with an unguarded `sessionStorage.getItem(FLAG)` and entry `setItem`; a storage refusal may abort construction of `window.YuikaParent` and break both mode and normal app initialization. This is a source-reading hypothesis, not a reproduced test result.
- Cleanup `remove(plan)` validates snapshots first, then writes multiple keys sequentially without rollback. A later write failure can leave earlier keys deleted. This is a source-reading hypothesis, not a reproduced test result.
- Banner says 記録・通知なし while containing an explicitly marked exception that deletes existing child data. README does distinguish the exception; adoption discussion should keep isolated trial and historical cleanup separate.
- Supplied tests cover normal isolated answers, reload/exit, mocks, inclusive deletion/cancel/stale confirmation. No test was run by PdM.

## Reconciliation and next work

- Record PR5/23 observed merged and PR6–8/14–21 observed closed separately from chat approvals. Do not leave them counted as open draft waiting work; do not claim live deployment verified.
- Retain existing REV-MVP/CONTENT-MVP/THEME-MVP CEO-wait tickets until their actual purpose/adoption is reconciled. Open extra PR22/24 are visible separate product work; no new product PR slot should be silently added.
- Recommended current-cycle outcome: independently review PR24 and record exact HEAD/evidence/defects in existing REV-RECONCILE. If reproducible defects, repair the same PR via coordinator and independent QA. No new product feature, no automatic close/merge.
- After safe trial verification, give CEO a synthetic-data trial path and ask for concrete usability feedback in normal checkpoint. Keep CONTENT-MVP next and THEME-MVP lower priority; Evernote real connection/storage remains D02.
