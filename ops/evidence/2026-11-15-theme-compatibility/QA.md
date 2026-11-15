# THEME-MVP 現main互換性 独立QA

担当 `qa_theme_compatibility`。実装者 `engineer_theme_compatibility` と別担当。最終固定HEAD **c81fb6b3a7e9c5c6c5d42431afe1d13a73c780d3**、2026-11-15T00:14:03.412251+00:00 にcleanを確認。製品/ops編集・push・本番操作なし。

## 判定

**限定レビューは成功、製品受入は未完（required_checks_pending）。** 新たな製品不具合は今回の検査範囲で観測していないが、必須23suiteと修正済みtheme全体の成功を確認していない。既存draftの未完候補として保存可能であり、merge/公開/利用者採用を承認するものではない。

Engineerのtheme検査は書き出し期待値で同原因2試行に達したため、PrMが今回の `tests/theme_review.py` / `scripts/check_all.sh` / export経路の再実行を停止した。独立QAもこれらを実行せず、別probeによるexport迂回もしなかった。過去57171adの4suite成功は現在候補の証拠に算入しない。

## 実施結果

- `static.py` 初回exit0。main86514edと旧PR12の57171adが候補の祖先であり、main差分はREADME、theme-spec、鎌倉HTML、theme test、check_allの5filesだけ。mainの既存embedded script4件、親runtime・通知block・CSPをbyte比較し一致。対象外HTML・共有design assets等は差分なし。runner差分はtheme test登録1行だけで、既存22suiteを保持する。
- mainから取り出したHTML/同一assetsを別loopback originへ置き、通常標準のbody/hero/見出し/説明/practice-card/startの6要素のcomputed文字色・背景・font-size・line-heightが一致することを確認。鎌倉選択で変わり、標準へ戻すと同じ値に復帰した。画面全体のpixel一致とは呼ばない。
- `scoped-probe.py` 2回目exit0、**14検査**。保護者確認モードのhome/quiz/feedback/result/保護者ノート/recordsを実UIで遷移し、両テーマで学習run/data/prefs/index/results/input/ヒント/採点・main DOM内容と先頭node identityが保持されることを確認。5合成回答は親セッションのprototype keyだけに保存され、通常localStorageのテーマ・旧記録・他単元・通知設定は不変。
- 親モードは通常テーマ値を読まず初期標準、セッション内テーマと合成回答はreloadで復元。終了buttonで親セッションキーを消し、通常テーマへ戻り、通常保存値は不変。実footerリンクから保護者ノートへ遷移できた。
- sessionStorage拒否時は既存一時メモリへテーマと1合成回答を保持し、通常保存値は不変。reloadで一時テーマ・回答が消える。通常localStorageへのfallbackは観測なし。
- 768×1024 Chromiumで6画面×両テーマの12画像を実際に表示して目視確認。検査した可視文字/背景68組は4.5以上（最低 **5.010**）、対象6画面で横overflowなし。ページ全体の可読性/長図/ネイティブzoom/実機Safariを保証しない。focus・44px/8px・print等はEngineerの限定証拠にあり、このQAでは反復していない。
- テーマ操作前後のresource追加0、結果画面の再enqueue0、POST到達0、pageerror0。既存Google FontsのCSS取得は遮断して別計数した。外部要求全体0やwebfont読み込み成功とは報告しない。全suiteは未実行で、このprobeの0送信を全suiteへ拡張しない。

## 初回probeの診断

初回は親結果画面まで通過後に通知spy件数assertで停止。QAの `page.evaluate('window.qaEnqueues=0;YuikaReports.enqueue=()=>{qaEnqueues++}')` が代入した関数を返し、Playwrightがその返値を実行して1加算した。返値のないcallbackに直した2回目で成功。製品編集なし、同原因3回目なし。初回ログ・スクリプト・途中結果は `attempt1/` と `scoped-probe-attempt1.log` に保持。Engineerのexport期待値失敗と別原因で、export実行は両回とも0。

## 静的なexport期待値照合と残件

最終theme testの期待値 `yuika-review-prototype` / formatVersion1 / payload.events は、現mainの `PROTOTYPE_FORMAT` と `prototypePacket` を読み取り照合した。製品の該当scriptもmainと同一。ただしダウンロード・JSON内容の動的な最終検証は未実行なので、成功へ置き換えない。

次runで固定候補HEAD・remote leaseを再確認し、修正済みtheme検証と全必須23suiteを実行して結果を保存する。未知値/read-write例外/回復/別画面往復等の最終theme検証後半も未完。現在候補を成功済み製品へ変更しない。実機Safari/iPad、本人嗜好・学習効果、公開動作は未検証。

手動venv再利用を使用し、自動snapshot引継ぎ・platform定時実行成功は主張しない。合成データのみ。本番merge/deploy/実通知/課金/Secrets/共有変更なし。

## 証拠範囲

`static-result.json`、`scoped-probe-result.json`、`final-result.json`、ログと12画像、実行した2スクリプト、初回ハーネス証拠を保存。未実行の初期準備probe、baseline checkout、__pycache__は公開証拠から除外。比較基点はmain86514edのkamakura-review.htmlとassets/design.css・design.js・progress.jsをgit showで取り出したもの。保存scriptを再現する際はOUT/baselineにこれらを復元する（本サイクルでの追加再実行は禁止）。SHA256SUMSは上記の公開証拠23ファイルの同一性を示す。
