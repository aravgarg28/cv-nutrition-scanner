# Build Sequence

Exact order. `∥` = parallelizable lanes. Checkpoint legend: 👤 owner decision ·
🎓 ML evaluation gate · 🛡 safety review · 🔒 security review · 🚀 deployment gate ·
🧠 senior review.

## Phase A — Foundation (R0)
1. T-001 scaffold → 2. T-002 CI → 3. T-003 compose
4. T-004 enums/envelope 🧠 → 5. T-005 client-gen
   - 👤 **Checkpoint A:** ALLERGEN_POLICY copy freeze v1 (before any UI/matcher work).

## Phase B — Walking skeleton (R1) — three lanes
**Lane 1 (backend):** 6. T-006 → 7. T-007 → 8. T-008 🧠🔒 → 9. T-009 →
10. T-010 🧠🛡 → 11. T-011 → 12. T-013 → 13. T-016 → 14. T-017 🧠 →
15. T-014 🧠🔒 → 16. T-015 → 17. T-025 👤🧠 (mapping+hints curation review) →
18. T-028 → 19. T-029 🧠
**Lane 2 (ML, ∥ from step 4):** T-018 👤(license memo) → T-019 → T-020 🧠 →
T-021 → T-022 🎓 → T-023 🎓👤 **Checkpoint B: architecture pick (AD-2)** → T-024 →
waves 2–3 continue ∥ → T-026 → T-027 🧠🛡 (thresholds)
**Lane 3 (mobile, ∥ from step 5):** T-030 → T-031 🧠🛡 → T-032 → T-033 → T-034 →
T-035
**Deployment lane (∥):** T-059 after T-017+T-027 exist 🚀 staging live
- 🎓 **Checkpoint C:** Wave-3 gate → serving candidate + τ/τ_u chosen; 3-seed final
  run; test-set evaluation; model card v1 🧠.
- 🚀 **Checkpoint D:** R1 smoke on staging; E2E scenario 1–4 pass; owner demo.

## Phase C — Allergen core (R2)
20. T-036 → 21. T-037 👤(fixture-corpus capture chore) → 22. T-038 →
23. T-039 🧠🛡 **the** safety review → 24. T-040 → 25. T-043 ∥ T-044 →
26. T-042 🧠🛡 → 27. T-041 👤 **Checkpoint E: panel scoping ratification (AD-1 🟡)**
→ 28. T-054 🔒 → 29. T-055 🔒🧠
- 🛡 **Checkpoint F:** full ALLERGEN_TESTS + E2E scenarios 5–7, 11 green; HUMAN_
  FACTORS review of evidence screens with 2–3 friendly testers; findings recorded.

## Phase D — MVP completion (R3)
30. T-012 → 31. T-045 → 32. T-046 → 33. T-047 🧠🔒 → 34. T-048 →
35. T-049 → 36. T-050 👤🧠 **Checkpoint G: LLM provider terms verification** →
37. T-051 🧠🛡 → 38. T-052 → 39. T-053 → 40. T-056 → 41. T-057 → 42. T-058 →
43. T-060 🚀 → 44. T-062 → 45. T-063 🧠
- 🛡🔒 **Checkpoint H (beta go/no-go):** AI_EVALUATION live tier; injection suite;
  deletion sweep test; OWASP checklist pass; all E2E scenarios; owner approves real
  testers.

## Phase E — Beta operations + research (R4/R5)
Monitoring cadence live (MONITORING); beta feedback → fixtures; R4 planning
checkpoint 👤 scopes T-070+ research cards; Wave-4 experiments (E14–E16) 🎓.

## Standing rules
- 🧠 senior-review tasks may not merge on Implementer's own approval.
- Safety-surface PRs (SAFE-A) carry the safety checklist in the PR description.
- Any real-world allergen miss → fixture-first fix (ALLERGEN_TESTS policy) 🛡.
- Sequence changes get recorded here with a dated note.
