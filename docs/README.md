# SnapNutrition — Documentation Index

Planning package produced 2026-07-12. Start here:

| Read order | Doc | Why |
|---|---|---|
| 1 | [decisions/DECISION_LOG.md](decisions/DECISION_LOG.md) | Binding decisions D0–D24 + guardrails |
| 2 | [product/MVP_DEFINITION.md](product/MVP_DEFINITION.md) | What we're building first |
| 3 | [safety/ALLERGEN_POLICY.md](safety/ALLERGEN_POLICY.md) | The normative safety surface |
| 4 | [execution/BUILD_SEQUENCE.md](execution/BUILD_SEQUENCE.md) | Exact implementation order |
| 5 | [execution/IMPLEMENTATION_HANDOFF.md](execution/IMPLEMENTATION_HANDOFF.md) → [FIRST_TASK.md](execution/FIRST_TASK.md) | How implementation sessions run |

Sections: `current-state/` repo assessment · `decisions/` decision log ·
`product/` vision, personas, journeys, MVP, features, roadmap ·
`safety/` safety model, allergen policy, medical boundaries, human factors ·
`ml/` problem definition → model card (10 docs) · `ocr/` OCR architecture + parsing
+ tests · `data/` nutrition sources, normalization, calculation, ontology ·
`ai/` assistant, RAG, tools, injection defense, evaluation · `portion/` options,
MiDaS assessment, evaluation protocol · `architecture/` backend, API, jobs,
inference, ONNX, data model, storage, images, repo structure, ADRs ·
`mobile/` app architecture, 15 screens, camera UX, offline · `security/` threat
model, auth, uploads, privacy, secrets · `deployment/` AWS + free-tier, envs,
docker, IaC, cost · `performance/` + `reliability/` budgets, benchmarks, failures,
observability · `mlops/` tracking, registry, pipeline, monitoring, feedback ·
`testing/` strategy, ML/allergen/E2E suites · `demo/` scenarios, scripts, data ·
`build/` local dev, CI/CD · `execution/` epics, graph, tasks, sequence, allocation,
handoff · `presentation/` README plan, résumé bullets, interview guide ·
[ADVERSARIAL_REVIEW.md](ADVERSARIAL_REVIEW.md) — 7-persona review + applied
revisions.
