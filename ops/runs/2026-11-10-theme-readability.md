# THEME-MVP：読みやすさの追加試用

2026-11-10 JST。運用正本 `14a8608236e8137f5d21aed04cb9fb630e9cf891` の4文書を読み、クラウド provider=cloud / running / 最新観測を確認。通常pushで `cycle-20261110T0000Z` のleaseを取得した。
既存PR #4〜#12とmainを照合。REV/CONTENTに新しい人の修正依頼はなく、次優先のテーマを確認した。

## 成果と判断

学習中に配色が読みづらく感じたとき、回答を保ったまま標準へ戻せるかを追加試用した。
対象は既存draft [PR #12](https://github.com/naoyanakajima-cyber/yuika-study/pull/12)、commit `57171ad9cab02fec6a080ecbe317fe11d3f51dcf`。
独立QAの確認範囲では、新しい製品修正を必要とする具体的な障害はなかった。製品コード・仕様・依存・CIは変更せず、追加証拠を運用PR #9へ保存する。
D05の方向性採用は維持し、同じ判断を再要求しない。試作品確認待ちへ戻す。マージ・公開は未承認。

## 担当と範囲

- PdM `pdm_theme_readability`：仕様T1〜T11と前回QAを読み、通常全回帰を反復せず、長文の読み比べ・読書位置から標準復帰・拡大相当の探索を提案。読取のみ、テスト未実行。
- PrM `root/coordinator`：範囲を確認し、独立checkout準備・証拠と画像の照合・報告を担当。
- 独立Reviewer/QA `qa_theme_readability`：重点browser probe、画像目視、HEADとclean状態を確認。製品編集なし。
- 実装修正の必要がなかったため、Engineerは今回起動しなかった。子2名、製品実装0件、子のpushなし。

独立checkout `/workspace/yuika-theme-readability-20261110` をPR #12のHEADから作成。mainは `d526d65fbae116f834d14ad994a27bc50ca23b62` のまま。
`bash scripts/cloud/setup.sh` はexit 0。Python 3.12.14 / Node.js 24.19.0 / Playwright 1.62.0 / Chromium 154.0.8037.57、pip checkと実起動成功。
これは手動準備であり、snapshot自動引き継ぎや定時実行プラットフォームの成功を確認したものではない。

## 今回の検証と限界

```bash
source scripts/cloud/activate.sh
python /workspace/work/theme-readability-qa-20261110/probe.py
```

最終probeの終了コードは0。ただし下記の遷移先照合で有効な検証範囲をhome/feedbackへ限定した。

- 768×1024で標準/鎌倉のホームと既存の長い解説（問題54025-38、合成誤答）を比較。本文・文字サイズ・行間・学習DOM・回答状態・テーマ以外の保存情報を保持。
- 横はみ出し・対象文字切れ・JavaScript例外・外部要求・POST到達は0。新規context、CSP `connect-src 'none'` を維持。
- 通常homeの見た目欄はy=93〜202px。解説を読むscrollY=156ではボタンが画面上方へ外れる。明示的に上へ戻り、キーボードで標準を選択して回答保持・可視focus・再読込後の標準を確認。上部へ戻る操作自体は仕様通りで、固定UIは追加しない。
- 追加探索は384×512 CSS px、DPR 2。200%ズームに近いレイアウト条件として、折返しと標準復帰を確認。ブラウザー固有のズームや実機iPad/Safari検証ではない。
- QAは有効なhome/feedback画像を4枚目視し、統括も拡大相当homeと通常feedbackを確認した。

初回probeは対象問の差替え後に通常の`prepare()`を呼ばず、古い選択肢が残るハーネス不備でtimeout（exit 1）。`prepare()`→`quiz()`へ修正した2回目がexit 0。製品、assert、CSPは変更していない。

統括の証拠照合で、parent/recordsと名付けた画像がfeedbackのままである点を指摘。QAがコードと画像を再確認し、未完runからの遷移確認dialogを処理していないため、画面遷移を確認できていなかったと訂正した。この2画面の今回成功主張を撤回。8画像を有効証拠、他8画像を除外・監査用として保存し、再実行はしていない。
これはQAハーネス/報告範囲の訂正であり、アプリの遷移不具合とは判定しない。前回の4コマンド成功は過去証拠として保持し、今回再実行したとは扱わない。

ローカル証拠：`/workspace/work/theme-readability-qa-20261110/` の `probe.py`、訂正版`QA.md`、`result.json`、画像。JSONの最終状態は `passed_for_home_and_feedback_only`。
製品checkoutは開始・終了時clean、HEAD不変。実機iPad/Safari、CEO本人の操作、好み・学習意欲への効果は未検証。

## 次の一手

REV/CONTENT/THEMEは改善・追加試用を終えて試作品確認待ち3件。次回は正本の具体的な修正依頼・CEO判断の取り込みを確認し、独立して進められる仕事がなければ終了する。時間を埋める全テスト反復や新機能追加はしない。D01/D02の実入力経路と非公開保存先は未決のまま。
既知の外部プレビュー失敗は継続。PR #11の更新HEADにもbotがBuild Failed、URL空欄を報告している。新しい実行ログは取得しておらず、原因調査や再デプロイは行わない。
実通知、マージ、アプリ公開/デプロイ操作、Secrets・課金・アクセス権・共有範囲・スケジュールの変更なし。停止中の旧自律更新も再開していない。
