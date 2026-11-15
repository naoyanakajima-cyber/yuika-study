# cycle25 Engineer：模式図ラベル contrast修正の実現性

読み取りのみ。候補c81fb6b、製品/テスト/ops編集・実行・pushなし。

## 観測した構造

kamakura-review.htmlのtree()は、各boxをrect直後のtextとして生成する。将軍/執権（北条氏）の2boxだけがfill=#b57c65、文字はfill=white/font-size=13。鎌倉/地方は#64736e、その他は#386455で別属性。模式図はrole=imgでaria-labelが「鎌倉幕府のしくみの模式図。」から始まる。共有design.cssにこのSVG fillを変える規則はない。

## 最小案

鎌倉HTML内のテーマ用styleに次の1規則をscreen限定の外へ追加する（標準/鎌倉/printすべて対象）:

```css
svg[role="img"][aria-label^="鎌倉幕府のしくみの模式図"] rect[fill="#b57c65"]{fill:#8f4f3c}
```

同図の2boxのみを濃い茶色へ変更する。文字内容・白文字・文字サイズ・図の配置・線・他box・DOM属性・main内学習script・問題/正解は変えない。CSSはSVG presentation attributeより優先するため、共有assetやtree()本文を編集せずに適用できる。背景色は候補であり、実computed fillによるsRGB比4.5以上を独立検証して確定する。

これは「標準の見た目をmainと完全一致」の厳密解釈には2boxの色だけの例外が必要。標準を含む不足contrastを修正するとのPrM/PdM範囲確認を記録する。それ以外の標準Design C・学習script byte一致境界は維持できる。C6の可読性を満たすための限定修正として扱い、全SVG/共有色の変更へ広げない。

## 意味のある回帰検査

実UIで標準/鎌倉を選び、上記aria-labelのSVGを1件特定。SVG textのtextContentが「将軍」「執権（北条氏）」の2件を特定し、それぞれ直前のrectが実際に背景であることとfill属性#b57c65を確認。getComputedStyle(text).fill とgetComputedStyle(rect).fillからcontrastを計算し各4.5以上を要求する。ラベル2件の存在/内容/13px、その他boxのcomputed fill不変も確認する。printも同じ2ラベルの比を確認すると、screenだけ適用される誤修正を防げる。問題配列・学習script末尾はmainとのbyte比較を継続。

元の不足はQAが観測したものを参照し、本確認で再試験・成功主張はしていない。QA終了・PrM明示許可後にのみ編集可能。

確認時刻: 2026-11-15T01:11:01.091797+00:00
