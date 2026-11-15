# Cycle32 independent QA: externally updated main

担当 qa_theme_compatibility。運用source b35eef2、lease78358b2/run cycle-20261115T080614Zの下で、PrM採択PdM条件を読み取り確認。対象は独立detached checkout `/workspace/yuika-main-reconcile-20261115`、固定HEAD **60d1a946cc02ed8acea54c0d7af7d6451fcc30ec**。製品/ops編集、commit/push、merge、公開・デプロイ、実通知、設定変更、新子起動を行っていない。

## 判定：現main照合の限定範囲は独立QA合格

現HEADの必須25suiteを初回実行し25/25成功、308秒、08:15:55 UTC完了。前後HEAD一致・working tree clean。独立限定probeは初回exit0で4/4条件成功。問題オブジェクト/キーの静的互換性と次回PR10仕様の限定レビューも成功。作者報告の3回成功や前サイクルの成功を今回の実行数へ算入しない。

## 独立probeの実施範囲

768×1024 Chromium、毎回fresh context、合成回答のみ。メダカ `medaka-07` と江戸 `edo-01` を通常/保護者モードで各1例、計4ケース。代表問題を1問sessionへ設定した後、入力・選択・確定は実UIを操作。全問題をもう一度解いた検査ではない。

- 初回誤答→選択肢提示の時点でイベント数・保存rawは不変。再読込しても未確定イベントは保存されない。
- 選択肢で正解して最終確定するとイベントが1件だけ増える。`correct=true`、`recallOutcome=assisted`、最初の合成誤答・最後の正答・`hintUsed=true`が同じ1イベントに保存される。
- 確定ボタンのdisabledを確認し、submit関数を追加2回呼んでも件数不変。再読込後も重複なし。これは多タブ同時確定競合の検証ではない。
- 元保存イベントの正誤を変えず、読み取りprojectionだけ`correct=false`となり、弱点候補と日次の先頭に残る。projection/集計を呼ぶ前後でstateと保存rawが完全一致。
- 理科の通常ケースでは、従来選択式の正解イベント（版番号なし）と新recallイベントを同じ履歴に混在。旧イベントは完全一致し、`firstResponse`/`recallOutcome`を追加されず、投影後も正解。江戸には旧方式の問題がないため旧/新混在を江戸で検証したとはしない。
- 全4例のホーム要約weakCount=1・due=0。旧正解を含む理科通常だけcorrect=1、他3例correct=0となり、選択肢正解を自力正解に数えない。日次は弱点1＋通常4。
- 親モード2例では、本人localStorage全体の文字列が入口前後で一致。新回答は親保存領域のみ。通常モードの保存を含め、実データは扱っていない。
- `firstResponse`欠落の不正JSONはvalidateStateが拒否し、元保存rawは不変。実UIによるファイルインポート全経路をこのprobeで網羅したという主張ではない。
- POST要求0、pageerror0。外部GETは遮断。全suiteは公開JS GETとmock通知を含むので、probeの通信結果を全suiteの0通信保証へ転用しない。

合成PNG4枚を保存し、メダカ通常・江戸親の2枚を独立目視。選択肢正解、最初/最後の回答、再確認対象の説明、親バナーを確認。全画面/全図の可読性保証ではない。

## 必須suiteへ委ねた既存境界

追加の同一試験反復を避け、現HEAD全suite内の直接assertと結果を利用する。

- medaka: 新17問のデータ構造/版、74件の実UI結果、図の各ひれ領域、別表記、結果とfirstResponse/hintUsed矛盾拒否、再読込、assisted→weak→unaided→再確認/日次/ホーム。
- edo: 新22問の実UI結果、版、別表記、矛盾拒否、未確定中断、assisted/incorrect→弱点→unaided→再確認、本人記録を保持した親unaided操作。
- history_compat: 対象アプリの全版・正誤・版番号有無を検証、旧イベントフィールド・過去採点・重複処理・元raw保全。変更前67問の履歴を新しい自力回答へ遡及変換しないことを補足混在probeでも照合。
- parent_mode: 全HTMLの親境界、本人領域隔離、再読込、通知抑止等。江戸の実回答は専用edo suiteで、追加assistedの通常/親2単元は今回probeで確認。

## 静的互換性

比較基点は前回検証済69f77d671b66484b501f7a0f5c292bfa96a22273。理科の旧67問は解析後オブジェクトが全て一致し、削除IDなし、新規medaka-01〜17のみで84問。応仁30/鎌倉38/平安75/重点46問も旧問題オブジェクト全一致。既存5アプリのKEY/LEGACY_KEY/OLD_KEY/PREF_KEY/SCIENCE_PREF_KEY定義の非空抽出結果が一致。KEYはカンマ区切り宣言のため初期正規表現を修正し、空配列同士の一致を証拠にしない。これは静的抽出の修正であり製品の試験失敗や再試行ではない。

読み取りadapterとホーム生成はrecallだけunaidedを復習正解へ投影し、保存のcorrectを直接書き換えない。未知unitを実在単元だけで絞り込むguardも維持。新教材の全科学/歴史事実の独立再校閲、全保存キー式の網羅的意味解析は今回の範囲外。

## PR10後続候補仕様レビュー

`docs/product/daily-count-spec.md` 末尾「2026-11-15：外部main更新後の互換性追従（未実装）」を読み取りレビュー。重大指摘なし。現mainとPR10の以前のQAを統合候補の成功扱いにせず、旧PR10の理由付きおすすめ/名称/実数、新mainの問題・履歴validator・二段階投影・未知unitguardを保持する。両系列の必須試験と代表UI境界を新固定候補で独立QAする条件が明確。PR11/12は後続で、画像/テキスト入力完成やテーマ全画面拡張を意味しない。改訂後の同サイクル18分条件・未完checkpoint・江戸再生成条件も再読し、main成功と候補成功を分離したままと確認。

## 準備・限界・外部状態

既存verified venvのbinリンクをignored `.venv` 内へ手動再利用し、requirements-dev一致を確認。製品ブラウザー試験は全て正規activateを使用。自動snapshot適用成功とは報告しない。今回probeは初回成功、製品修正なし。

外部PR27/28/29のマージは観測された外部行為で、この担当が実施/承認したものではない。現mainのPages/Workers API成功は統括の読戻し情報で、過去PR27時点のWorkers失敗とは別。ここでは公開ページを取得しておらず、公開画面の動作成功を保証しない。正本CEO返答の取り込みやPR10/11/12の採用を推測しない。

実機iPad/Safari/WebKit、本人の学習効果、公開先実画面、他PRとの統合、実資料入力は未検証。2つの代表text recallの結果を全図/全入力/多タブ競合へ一般化しない。PrMは途中で同サイクル継続条件を追加した。現main QA成功後18分以上残れば既存PR10の独立候補へ進め、候補の独立QA未完なら未検証コードをPRへpushしない。08:15:55時点で条件を満たす旨を統括へ通知した。このmain報告を候補のQA成功へ転用しない。

証拠は `/tmp/yuika-cycle32-qa/`。実行stdout、前後HEAD/clean/時刻、実行probe/JSON、合成PNG、静的比較、仕様レビューを保存。SHA256SUMSを全suite終了後に生成した。
