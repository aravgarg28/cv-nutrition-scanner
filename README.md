# SnapNutrition

<!-- Replace OWNER with your GitHub username/org once the repo is pushed. -->
[![CI](https://github.com/OWNER/snapnutrition/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/snapnutrition/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

> Photograph food, ingredient labels, nutrition panels, or barcodes and get
> **evidence-typed** nutrition and allergen information — that never pretends to be a
> guarantee.

A portfolio-grade, full-stack computer-vision nutrition & allergen scanner:
fine-tuned Food-101 classifier (ONNX CPU serving), OCR ingredient/label pipeline,
an evidence-typed allergen engine, and a grounded assistant — behind an Expo React
Native app and a containerized FastAPI backend, on an all-free-tier stack.

**Status:** early implementation. Planning is complete; the build follows
[`docs/execution/BUILD_SEQUENCE.md`](docs/execution/BUILD_SEQUENCE.md).

## Core principle

The app communicates uncertainty honestly. It never says a food is "safe" or
"allergen-free"; it shows *what it observed, what it retrieved, what it predicted,
what you told it, what it estimated, and what it could not determine* — separately.
See [`docs/safety/`](docs/safety/ALLERGEN_POLICY.md).

## Documentation

Full design lives in [`docs/`](docs/README.md). Start with the
[Decision Log](docs/decisions/DECISION_LOG.md), the
[MVP Definition](docs/product/MVP_DEFINITION.md), and the
[Allergen Policy](docs/safety/ALLERGEN_POLICY.md).

## Repository layout

```
apps/       api (FastAPI), mobile (Expo), web-demo
packages/   shared-schemas, nutrition-core, allergen-core, preprocessing
ml/         datasets, training, evaluation, export
data/       corpus (RAG), seeds
docs/       design documentation
```

See [`docs/architecture/REPOSITORY_STRUCTURE.md`](docs/architecture/REPOSITORY_STRUCTURE.md).

## Local development

Prerequisites and full setup: [`docs/build/LOCAL_DEVELOPMENT.md`](docs/build/LOCAL_DEVELOPMENT.md).

```bash
uv sync                 # Python workspace
pnpm install            # TS workspace
uv run pytest           # tests
uv run uvicorn snap_api.main:app --reload   # API → http://localhost:8000/healthz
```

## License

[MIT](LICENSE). Nutrition data: USDA FoodData Central (public domain) and Open Food
Facts (ODbL, attributed). See docs for full attribution.
