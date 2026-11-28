# D01 合成チャット引き継ぎ：独立QA

対象製品HEAD: `3d2ed2f9a62673d2fb086a360ae841096f35b63e`。実行: 2026-11-10 21:26:51–21:26:55 JST。
初回試行・終了コード0。製品worktreeは実行前後ともclean。Chromium 154.0.8037.57、768×1024。

## 実行コマンド

```bash
cd /workspace/yuika-chat-handoff-trial-20261110
source /workspace/yuika-content-flow-20261110/scripts/cloud/activate.sh
python /workspace/work/chat-handoff-qa-20261110/probe.py > /workspace/work/chat-handoff-qa-20261110/run.log 2>&1
```

既存venvを明示有効化して利用。依存インストール・setup・環境設定変更なし。
テスト自身は製品のPreviewHandlerをephemeral loopback portで起動し、終了時に停止。
新規browser context、外部route遮断、通知CSP保持、合成storage sentinelを使用した。

## 結果

- **T1 成功**: 合成チャット受付に対応する既存テキストfixture JSONをファイルとして
  「保存した合成案JSONを再入力」(`#import`)へ渡した。原本/転記/問題項目の一致、
  案内移動による状態変更・DLなし、個別明示確認後の実JSONダウンロードを確認。
  実際に保存したbytesを再入力し内容保持と全確認失効を確認。再確認後のhint編集でもrevision+1、
  status=draft/confirmedRevision=null、確認済み出力不可となった。
- **T2 成功**: 判読不能な合成画像案を同じ入口へ渡し、同梱SVGと不明箇所表示を確認。
  読み取り欄は空のまま、answer/null・uncertainty/resolution/nullを補完しなかった。
  内容確認・確認済み出力はdisabled。未確認案を実ダウンロードし、そのbytesを再入力して
  元IMAGE fixture全体と完全一致、未解決・未確認の保持を確認した。
- **T3 文書レビューのみ**: 指定外のチャット資料/範囲は試用対象外と説明し、架空のJSONや
  OCR/生成成功を作らないという仕様を確認。自然言語parserや非対応sourceのUI試験は行っていない。
- 外部要求0、遮断route発生0、POST到達0、アプリstorage書込0、合成履歴sentinel保持、JS例外0。
  確認した各状態で横はみ出しなし。Navigation対象のfocusとviewport内表示もassertした。

## 文書の独立レビュー

統括が追加した `docs/product/chat-intake-spec.md` の「JSONを渡す画面と操作」を確認。
画面パス・入力欄ラベル/id・fixture非配信・JSONのみの引き渡し・画像の未解決保留・
公開URLではないこと・手動模擬/CEO試用との区別は、実UI・サーバー実装・今回の結果と整合。
重大な指摘なし。レビュー時の文書SHA256: `c02e6fada2706023d6f038913324012ad4ee5c9becad3eb84d240b6ca53070da`。

## 成果物

- `probe.py`: 再実行用probe。製品ソースは変更しない。
- `result.json`, `run.log`: 実行結果。
- `confirmed-content-proposal.json`, `draft-content-proposal.json`: 実際にbrowserでダウンロードした合成案。
- `text-confirmed.png`, `text-reimport-unconfirmed.png`: 確認済み/再入力後の未確認。
- `image-held-draft.png`, `image-draft-reimport.png`: 不明箇所を保留/再入力後も未解決。

## 限界

既存合成fixtureを担当エージェントが手動で渡す模擬引き継ぎ。
チャット→画面の自動接続、OCR、自由文からの問題生成、Evernote接続、実教材、CEO本人の使い勝手、
iPad実機Safariは未検証。問題案を学習アプリへ導入していない。製品コード不具合は再現せず。
全回帰テストは反復せず、この新しい引き継ぎシナリオだけを検証した。

## 統括の保存・担当・次の一手

run `cycle-20261110T1223Z`。起動時にprovider=cloud/running/最新観測を確認。
正本の初期commit `9f467e5e4d5dcd349001c2621c7c5025937bc204` からleaseを通常pushで取得。
PdM `pdm_chat_handoff_trial` がT1〜T3の範囲と手順不足を特定し、PrMが確認後に
独立QA `qa_chat_handoff_trial` が実施した。製品不具合がないためEngineerは起動せず。

手順書補足commit `0469148f1d0b9c1924c0b9a4d2e32f4884a12bb2`。
統括はレビュー済み文書SHA256との一致を確認し、テキスト確認済み・画像保留のPNGを視認した。
手順書と本報告は運用draft PR #9へ保存。製品PR #11のHEADは変更せず、第4の製品PRは作らない。
既存venvの明示activateを利用し、pip checkは終了0。自動snapshot引き継ぎの再検証ではない。

D01のチャット入力は採用済み。D02のEvernote候補・実データ接続・保存先は未決のまま。
この試用では実データを取得せず、Evernoteを呼び出していない。本番変更・実通知・権限変更なし。
次はREV優先を維持し、CEOの具体的な操作フィードバックを既存PRへ返す。
教材側の合成引き継ぎ手順は検証済みなので、新しい理由がなければ同じ試験を反復しない。

## 実行成果物の照合用hash

成果物はクラウド内 `/workspace/work/chat-handoff-qa-20261110/` に保存。
PNGは合成教材のみ。ローカル成果物の継続保持やCEO端末への引き渡し成功は保証しない。
検証結果と操作手順はこのGit文書に保存する。

| ファイル | SHA256 |
| --- | --- |
| `QA.md` | `a394e482b801c9e5a5bcc0a49a0a72e2123e3c6299d1df99d0e85206ce72cfe4` |
| `confirmed-content-proposal.json` | `5c331641745f218fc1f7dae9b21ba8dc52c1bb0c75ff633e874d9e032566519c` |
| `draft-content-proposal.json` | `cd4ccacf396ab4bbb588c7837dfcb15128d3a5e4f8466e05fa72d7868b01b0e8` |
| `image-draft-reimport.png` | `b0809fdf3efa8e571df8eba191dbed2279572120aecb8b1ad0a6187a82086b1e` |
| `image-held-draft.png` | `b0809fdf3efa8e571df8eba191dbed2279572120aecb8b1ad0a6187a82086b1e` |
| `probe.py` | `ad994beb3390c591121c71c2eb3f5217382303e7ff1c2a54d3a3bc2baa6a100f` |
| `result.json` | `1451f62d832ca2b0718ec7225d24ae2bf604bf5f33cd110940b456021d7c5c7c` |
| `run.log` | `42e9ef6aa27f16c3e31bc83427e8dc068f1c04b4a3b1afeb425b680c39ef9f1e` |
| `text-confirmed.png` | `40989634abb807569449daf1c7f0e1abe35338954ae18fff79fbc37d5f93d31c` |
| `text-reimport-unconfirmed.png` | `da6d568399eb1395362a36d5a6ff63f79492b341d3ce79cd070de4340792878f` |
