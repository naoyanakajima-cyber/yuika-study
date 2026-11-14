# PR25 home summary validation repair

Engineer: engineer_design_summary. Base 81002855830dda7d2cac669f8297a0d81756872d; candidate 042c55dd04a285277dc3dfa9dd296f161283e809. Independent checkout /workspace/yuika-design-fix-20261112; no push or PR update by child.

Reproduced QA bugs: an invalid history envelope was presented as valid zero-history/normal-five counts, although the unit loader blocks daily review; unsupported saved variants were used by home instead of falling back to the unit's normal variant.

Changed only scripts/design/build_summary.py, its generated assets/progress.js and tests/design_c.py. Generator extracts the unit's exact pure history loader validation and helpers, including historical question revisions, grade consistency, date/type checks, duplicate identity, and science legacy metadata. It validates before projecting counts. Only missing storage (null) uses the unit's actual empty state. Empty strings and malformed JSON/records return null for existing safe home fallback. It never saves, deletes, migrates or rewrites the raw history. Historical grading is invoked only for existing validation parity, not to alter a saved grade. Allowed variants derive from each unit's own declaration/fallback array.

Regression additions exercise all five units: empty string/bad JSON/missing schema/wrong dataset/unknown question/wrong grade/unknown revision/conflicting duplicate; invalid science legacy metadata; valid identical duplicate; preserved raw bytes and no summary write/delete calls. Three unsupported variant fixtures must match normal fallback. Existing design tests still cover default synthetic due1/weak1/normal3, all14 home units, five standalone entries,390/768/1024px, controls and recipient privacy.

Validation performed by Engineer:
- node --check assets/progress.js: exit0.
- generator repeat: identical SHA256 b19a03b7c02d41d37f8f82a9d10e4f2e301160ae12f2e9f82adb3c52c68960bc.
- git diff --check: exit0.
- Activated focused tests/design_c.py: exit0 before variant additions; final run after variant additions also exit0 (/tmp/design-engineer-test-final.log). No full suite by Engineer; independent QA is separate.
- Initial direct-Python invocations of design_c and the QA probe failed before browser execution because activate.sh was omitted and no Playwright-managed browser existed. Diagnosed and sourced the existing prepared activate.sh to select /usr/bin/chromium. No dependency/browser install or permission change performed. The QA probe was not rerun by Engineer after this setup error; QA retains baseline/probe responsibility.

Tradeoff: generated summary asset grows from 28,925 to231,306 bytes (gzip4,630 to50,569) because it includes the existing public question revision data needed to validate historical records. This avoids a new approximate validation contract. No private data was used. The exact generated snippets depend on the current standalone helper names/one-line const declarations; regeneration fails if required helpers are missing. Real iPad/Safari is not tested here.
