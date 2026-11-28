# Synthetic visual inspection

Reviewer `qa_theme_pr32` directly opened all six PNGs produced at candidate `b4deb0df131b1280ab2cc0647851e1d345d06143` on 2026-11-27. Fresh Chromium contexts used a 768×1024 viewport; labels, answers and records are synthetic. Screenshot inspection supplements, rather than replaces, computed-style and state assertions.

- `normal-kamakura-hint.png`: selected Kamakura button, input answer, hint and grading action are readable and separate. The cream background and dark blue controls render consistently; no overlap or clipped text in the captured main area.
- `parent-kamakura-hint.png`: persistent parent banner is visible above the same theme, input and hint. Main learning controls remain readable and separate within the viewport.
- `normal-math-result.png`: math keeps its existing blue header and pale neutral background. The stage-two 3/3 synthetic result and navigation controls are readable; no theme panel appears.
- `parent-math-result.png`: parent banner and math result coexist without overlap. The math appearance remains unchanged; no theme panel appears.
- `kamakura-diagram-screen.png` and `kamakura-diagram-print.png`: both hierarchy labels, surrounding nodes, connecting lines and explanatory text are legible. The two darkened hierarchy backgrounds and all label geometry match. Computed contrast for the two hierarchy labels is 6.265720821251096 in both themes and both screen/print media, exceeding 4.5.

Root/coordinator separately inspected `normal-kamakura-hint.png` and `parent-math-result.png` as a supplementary review. Browser print emulation is not physical printer verification. No real-device Safari/WebKit, user preference or learning-effectiveness claim is made.
