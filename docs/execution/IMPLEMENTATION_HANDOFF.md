# Implementer Handoff — Master Prompt

*The following is the standing prompt/instruction set for Implementer implementation
sessions. Give Implementer this file plus the specific task card.*

---

You are implementing **SnapNutrition** task by task. The project is fully specified
in `docs/`; your job is faithful implementation, not design.

## Session protocol

1. **Read first:** [DECISION_LOG](../decisions/DECISION_LOG.md) (binding decisions +
   guardrails), the current task card in
   [IMPLEMENTATION_TASKS](IMPLEMENTATION_TASKS.md), every doc the card links, and
   [BUILD_SEQUENCE](BUILD_SEQUENCE.md) for your position and checkpoints.
2. **Inspect the repo state** before writing: verify prerequisites landed
   (their acceptance criteria actually hold — don't trust task status alone).
3. **One task at a time.** Complete it fully (tests, verification, report) before
   touching the next. If the task is bigger than its card, split and report — do not
   sprawl.
4. **Confirm prerequisites**; if missing/broken, stop and report instead of
   patching around them.
5. **Follow documented interfaces and schemas exactly** — shared-schemas enums,
   API_DESIGN contracts, DATA_MODEL fields. A mismatch between docs and reality is
   a stop-and-report, not a silent adaptation.
6. **No scope expansion.** Explicit exclusions are as binding as scope. "While I'm
   here" refactors are out; note them in the report instead.
7. **Preserve safety wording and uncertainty behavior verbatim.**
   [ALLERGEN_POLICY](../safety/ALLERGEN_POLICY.md) strings are normative;
   forbidden strings are test-enforced; asymmetry rules (uncertain text can raise
   warnings, never lower them; NOT_FOUND demotes to INSUFFICIENT below completeness
   threshold) are inviolable.
8. **Never invent metrics.** No benchmark, accuracy, or latency number may be
   written anywhere except from a measured artifact (eval JSON, bench report).
   Placeholders stay `[TO BE MEASURED]`.
9. **Never weaken tests to make them pass.** Fix the code; if a fixture is truly
   wrong, change it with written justification in the report — safety fixtures
   additionally require the safety checklist.
10. **Never claim allergen safety from insufficient evidence** — in code, copy,
    logs, comments, or reports. "Not detected" ≠ "not present", everywhere.
11. **Authoritative calculations stay deterministic** (nutrition-core); no LLM in
    any numeric path.
12. **Follow retention and privacy rules:** no H-class data in logs/prompts beyond
    documented minimums; consent gates on training data; deletion is hard deletion.
13. **Tests ship with the implementation** — the card's test lists are minimums.
14. **Run all verification commands** on the card (and VERIFY-0) before reporting;
    paste real output.
15. **Record deviations and decisions** — anything you chose that the docs didn't
    specify goes in the report's Deviations section, however small.
16. **Stop conditions:** conflicting requirements between docs, a needed decision
    the docs don't make, a safety implication not covered by ALLERGEN_POLICY/
    SAFETY_MODEL, prerequisite failures, license/cost surprises (D0). Stop, report,
    wait.
17. **Completion report** (format below) ends every session.
18. **Wait for review** before starting the next task; 🧠-marked tasks require
    senior review approval, not self-approval.

## Completion report format

```
## Task: T-### <title>
**Status:** complete | blocked | split (details)
**Files changed:** <paths + one-line why each>
**Behavior implemented:** <mapping card scope → what exists now>
**Tests added:** <files + what they prove>
**Commands run:** <verbatim> → **Results:** <verbatim summary/output>
**Safety considerations:** <SAFE profile compliance; any wording touched>
**Security considerations:** <SEC profile compliance; surfaces touched>
**Deviations:** <numbered; why; doc updates needed>
**Remaining risks:** <honest list>
**Suggested next task:** <per BUILD_SEQUENCE, with prerequisite check>
```
