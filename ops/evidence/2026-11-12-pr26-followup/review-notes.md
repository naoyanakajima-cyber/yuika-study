# PR26 independent QA notes (in progress)

Reviewer: qa_pr26_review (independent of implementation).
Initial reviewed HEAD: 326d5fd76756963819fcdc0a7463ef867aeed331.
Cloud-only verification, synthetic fresh browser contexts, external browser requests intercepted/aborted. No install or external notifications.

## Finding confirmed and returned to Engineer
Unsupported subject values `constructor`, `toString`, and `__proto__` were resolved through inherited ordinary-object properties in focus runtime and home summary. They produced a function/object title and zero available questions instead of the all-46 fallback used by missing/empty/unknown subject. No code execution or storage loss observed. Reproduced once in subject_url_probe.py; evidence subject-url-baseline-results.json.

## Static review
Subject scoping wraps candidates, grouped history, weaknesses, retention and notes/TXT projection. Shared validated raw events and question/version IDs remain complete; JSON export/import preserves all four subjects. Home summary projects selected subject through the existing validator and retention functions. Distinct preference keys isolate valid subject settings from the old mixed route. Existing responsive regression covers 44 synthetic old/revision-1/review-v1 events, save/reload/import/export, 17 homepage entries, normal and parent modes, four viewport sizes, real and stable scrollbar gutters. CSS addresses layout instead of hiding horizontal overflow. Existing mixed-history and notification assertions remain in place.

## Independent probe prepared
preferences_probe.py covers actual UI changes of legacy/math/science counts and units, persisted separation, home summary consistency with selectable daily count, parent-mode preference isolation, navigation persistence, and normal-state restoration on exit. It will run only on the fixed candidate.

## Limits
Chromium/browser emulation does not establish Safari/WebKit or real-iPad compatibility. No production deployment or private records accessed. Full 22-suite completed on fixed candidate acd169882b626ef255ba68cd73c995024c30e515: every suite exit0, total332s, one run.

## Fixed candidate review
Engineer committed acd169882b626ef255ba68cd73c995024c30e515. Both subject lookups now use Object.hasOwn; generated runtime/summary agree. New regression tests empty/unknown/inherited subject values, all-46 fallback, mixed preference restore, home-summary equivalence and shared raw preservation. The prior parent-mode test repair seeds queued synthetic work on an inert same-origin fixture before app initialization, removing the app-startup flush race while retaining notification and isolation assertions.

Independent repaired URL probe passed all 8 cases on this exact candidate (subject-url-fixed-results.json): unsupported values fall back to all 46, valid social has 21, duplicate math-first has 6, normalCount 5, no page errors and no localStorage writes.

## Supplemental preference probe limit
The independent preference probe passed assertions before its exit wait: legacy mixed count15 stays separate; math/science each initialize count5/all/all/normal; actual UI count/unit edits restore independently; each subject summary count equals daily selectable count; parent math starts isolated, its preferences survive same-tab navigation, parent science remains independent, and normal localStorage remains byte-for-byte unchanged. It did not finish: attempt1 read YuikaParent during reload before initialization; attempt2 string-based wait_for_function evaluation was rejected by CSP. No product edits or CSP relaxation were made. Stopped after 2 attempts. Exact partial results are preferences-partial-results.json. Exit restoration and final pageerror assertion are unverified by this supplemental probe. The regular parent_mode suite separately passed isolation/reload/exit/notification guards for all six pages, including mock focus.

## Final disposition
No remaining blocking product finding in reviewed scope. Independent required check_all.sh: 22/22 suites exit0, total332s, one full run on acd169882b626ef255ba68cd73c995024c30e515. Candidate remained clean. Repaired URL probe8/8 passed. Suitable for coordinator to update draftPR26 within existing authority; no merge/publication approval implied. Preserve supplemental harness limit and Chromium-only limitation in evidence.
