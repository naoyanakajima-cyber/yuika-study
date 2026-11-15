# CONTENT-MVP 現main互換候補：独立QA

Reviewer `qa_content_trial_delivery`、実装者 `engineer_content_trial_delivery` とは別担当。cycle33、2026-11-15。正本規則・台帳・PdM7条件・PrM範囲を読取り、freeze連絡後だけ候補を検証した。製品/ops編集・push・公開・設定/権限変更・実送信なし。既存venvを手動有効化し、自動snapshot適用成功とは扱わない。

対象は独立checkout `/workspace/yuika-content-main-compat-20261115`、固定候補 `d75a5469fbf1e8c5011a6307308546e5ec669ceb`。旧PR11 `ee51e68d7e1eeb21bd0e959ec58166a869947d0a` と main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec` の両方を祖先として保持。試験開始時cleanを確認した。Engineerのfocused2suiteは独立QAの実行数へ加算しない。

## 独立差分・境界の確認

main相対差分19pathsを読み、mainの7学習HTML（江戸を含む）・assets・recall/履歴/復習・親runtime・通知コードを含む共有接点7paths以外の84filesを全てbyte比較で維持と確認。共有接点はREADME、docs/codex-cloud.md、check_all、serve、parent embed、cloud_preview、parent_modeだけ。生成元や採点・保存の意味変更を追加せず、PR10独自改善も採用していない。

旧PR11からcontent HTML・3仕様・4fixture・4専用testsの12pathsはbyte一致。content SHA256は `fea62d048857059b8016f3a36061795bacb18acf160d1bdc0c9997d277abd001` のままで、生成器と親preflightの例外はこの固定contentだけ。mainのrecall回答操作と江戸の必須存在検査が併存する。必須suiteはmain全suiteと旧PR11の4content suiteの和集合・重複なし、29件と直接照合した。

限定serveはmain側からcontent入口1件を足しただけで、それ以外のコードは一致。実HTTPでcontent/江戸GET 200、未知HTML/.git/fixture/API GETは404、HEADは405、APIへの合成loopback POSTは501、各応答のno-store/connect-src noneを確認した。これは外部通知の送信ではない。

固定候補のgit archiveを/tmpへ隔離し、parent generatorの正常実行で全HTMLがbyte同一（冪等）と確認。親preflightは正常候補を受理し、保護のない未知HTMLを拒否。content改変は生成器がHTML書込前に拒否し、親preflightも拒否した。未知HTML自体を生成器が拒否するという新仕様は要求していない。

## 限定合成UIの実測

fresh Chromium context、768×1024、同梱合成textだけで、サンプル選択→未確認時開始不可→個別確認→試し解き→「こおり」回答→採点→終了→案JSONダウンロード→再開始の未回答状態を実DOM操作した。採点画面の回答・一致結果・正答/読み・解説・終了ボタンを画像で目視。試行中editor非表示、開始時focus、終了でtrialと表示DOM消去を確認。試行前後のproposal/確認状態/unsavedは同一、JSONは元proposalと同一で試行情報なし。

probe監視範囲でStorage操作・history操作・IndexedDB/Cache/SW操作0、localStorage/sessionStorageは空、window.name空、非許可ブラウザー要求0、pageerror0。許可するブラウザー要求はloopback content GETのみ、その他はabortした。今回65ケースの独立旧probeは再実行していない。contentのbyte保持と候補での既存content4suite、および今回の変更接点probeを根拠とする。

HTTP probeで応答status/headers確認後に本文を読まずcloseしたため、サーバー側の送信途中BrokenPipeErrorが1件ログに残った。probeのassertと最終JSONは成功し、ブラウザーpageerrorは0。製品不具合や再試行による成功へ読み替えず、元ログを保持し、同じprobeを成功するまで反復していない。

江戸の親隔離は全suite内のtests/edo.pyで、合成保存履歴を用意し、?parent-check=1へ実遷移→実回答後のlocalStorage raw同一を検証する。tests/parent_mode.pyの実UI対象6appsと、江戸を含む7学習HTMLの静的必須境界を区別する。

## 限界・次の判断

合成データ・Chromiumのみ。実教材/本人の回答・本人試用・学習効果・Safari/WebKit/実iPad・実BFCacheヒットは未検証。全必須suiteには既存の公開JS GETとmock通知試験があり、全体外部要求0とは主張しない。外部Workers Buildsや本番公開結果もこのQAの根拠にしていない。

## 最終判定

2026-11-15T09:15:16.286978+00:00、固定HEAD `d75a5469fbf1e8c5011a6307308546e5ec669ceb` とcleanを再確認。必須全29suiteは初回で29/29・exit 0・325秒。静的/隔離負例と限定HTTP/合成UIprobeも各初回成功。blocking 0、**既存draft PR11更新・CEO判断待ちへ進める範囲でPASS**。本番マージ/公開承認ではない。全suite一覧・試行数は `final-result.json`、ログは `check-all.log`、独立静的/短いUI結果は `static-result.json` / `main-identity.json` / `probe-result.json`、実測画像は `trial-graded-768x1024.png`。製品編集はfreeze以降なし。次は統括が実行権/既存PRHEADを再確認し必要pushと台帳保存・lease解除を行う。
