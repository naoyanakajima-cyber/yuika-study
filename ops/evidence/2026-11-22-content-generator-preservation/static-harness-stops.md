# Static harness stops (not product suite failures)

Attempt 1 stopped at static.py line 25 because QA incorrectly expected text `allowed=` on the changed event-field row. Attempt 2 stopped at line 27 because QA incorrectly assumed `prototypeScience` used a pathname predicate. Actual code uses `typeof byId!=='undefined'` (runtime.js:3); the allowed branch is runtime.js:13–14. Both attempts reached successful content blob, unchanged science HTML and source/embedded identity checks; attempt 2 also confirmed the exact optional-field replacement on the first non-science page.

No third static bundle invocation. Read-only `git diff` and `rg` verify all four other HTML rows and predicate provenance. Still-unexecuted generation and old-base negative checks ran separately in regeneration.py. See static-readback.json for hashes and regeneration-result.json for executed outcomes.
