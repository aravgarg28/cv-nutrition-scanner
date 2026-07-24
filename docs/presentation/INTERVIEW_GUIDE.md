# Interview Guide

Prepared answers (owner should internalize, not recite). Each: the honest core +
the depth hook.

**Why EfficientNetV2?** — "I didn't assume it. I ran ResNet-50 as a baseline and
EfficientNetV2-S vs ConvNeXt-Tiny head-to-head under the same budget; the decision
metric was macro-F1 and calibration at equal CPU latency, because my serving target
was CPU. {Winner} won on {criterion}." Hook: progressive resizing, depthwise-conv
CPU behavior, the tie-goes-to-simpler rule.

**Why Food-101?** — Balanced, big enough for real fine-tuning, permissively usable,
and its noisy train labels are a feature for teaching label-noise handling. Hook:
license review memo, dedup findings.

**What's missing from Food-101?** — Most world cuisines, raw ingredients, packaged
foods, homemade presentation. "That's why I built a phone-domain eval set and report
both numbers — official test {x}%, phone-domain {y}% — and why OOV routing to 'not
sure' exists." Hook: cuisine-bucket F1 table, fairness disclosure in model card.

**Why top-5 accuracy?** — Because the UX is confirmation, top-5 measures "is the
right answer in the list the user sees". But alone it's insufficient: calibration
(ECE), per-class F1, and OOD behavior gate the release. Hook: EVALUATION_PLAN §why
top-5 is insufficient; allergen-weighted confusion pairs.

**How is calibration measured?** — 15-bin equal-mass ECE + reliability diagrams,
before/after temperature scaling fit on validation; T is baked into the ONNX graph.
Hook: why calibrated confidence matters when a UI frames results by threshold.

**Why ONNX?** — Decouples training from serving: torch-free 2.5 GB→smaller runtime
image, CPU-optimized inference, later mobile path from the same artifact — with
CI-enforced parity so the decoupling can't drift. Hook: metadata_props contract,
baked temperature, parity tolerances.

**Why FastAPI?** — Async-first (polling + external APIs), Pydantic contracts shared
with the client generation, OpenAPI for free. Honest: at this scale most frameworks
work; the win is the schema discipline.

**Why PostgreSQL and pgvector?** — One database as system of record, job queue
(SKIP LOCKED + transactional enqueue with the state machine), cache, AND vector
store for the RAG corpus — smallest honest infrastructure. Hook: why user content
never gets embedded (privacy boundary).

**What does RAG do here?** — Explanatory knowledge only: ingredient definitions,
allergen education, source docs — with enforced citations. Hook: the tools-vs-RAG
split.

**Why not RAG for numeric nutrition?** — Facts live in Postgres with provenance;
SQL is exact, auditable, and deterministic; embedding-and-retrieving numbers adds a
fuzzy layer exactly where errors are least acceptable. LLMs also don't do reliable
arithmetic — serving math is pure tested code.

**Why might Lambda be unsuitable?** — Interactive CV+OCR wants a warm model in
memory; Lambda cold starts (image pull + session init per concurrent instance)
land on users, and chaining classifier+OCR+RAG in one invocation couples worst
cases. Lambda fits the spiky offline jobs — that's where the AWS design uses it.

**How does OCR work?** — Pipeline: quality gate → label detection → perspective/
rotation → CLAHE → PaddleOCR det+rec → layout/section detection → grammar parsing →
confidence + completeness scoring. Hook: the asymmetry rule (uncertain text can
raise warnings, never absence) and the completeness→INSUFFICIENT demotion.

**Why is allergen safety hard?** — Synonyms (whey/casein), compound ingredients,
and/or lists, "may contain" semantics, OCR misses, cross-contamination that no
label shows — so the product's strongest claim is evidence-typed: "here's what we
read, here's what we couldn't." Never "safe". Hook: forbidden-strings tests,
fixture-first regression policy.

**How is uncertainty communicated?** — Typed information (observed/retrieved/
predicted/estimated/missing), calibrated-confidence framing with thresholds,
completeness indicators, and status wording that carries its own limits. Hook:
HUMAN_FACTORS (why NOT_FOUND is never green).

**How is portion size estimated?** — It isn't, automatically — FDC serving presets
+ manual adjustment, labeled "per selected serving". "I assessed MiDaS: monocular
depth is scale-ambiguous; shipping volume from one uncalibrated photo would be an
indefensible number. The R4 protocol (reference object + weighed ground truth +
pre-registered go/no-go) is written." Hook: MIDAS_ASSESSMENT — this answer is the
judgment demo.

**What would production require?** — Paid always-on compute (kill cold starts),
RDS/S3 with real backup posture, WAF, MFA, formal privacy review (the beta is
US-informal), pen test, wider label-format coverage, and a legal pass on
allergen-adjacent claims. Hook: AWS_ARCHITECTURE migration runbook exists.

**Largest technical limitation?** — The domain gap: a 101-class Western-skewed
dataset behind a camera pointed at the whole world of food. Quantified
(phone-domain eval), mitigated (OOV routing, confirmation UX, search rescue), not
solved. Second: OCR on curved/glossy packaging — mitigated by barcode fallback and
completeness honesty.
