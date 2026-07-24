# Cost Model

Budget: **$0.00** (D0). The cost model is therefore a *quota* model: every provider
must have hard-stop or no-overage behavior, and quotas are monitored like SLOs.

## Driver inventory & controls

| Driver | Provider/tier | Free quota | Hard-stop behavior | Control |
|---|---|---|---|---|
| API compute + inference + OCR | HF Space free CPU | Always-free CPU basic; sleeps | Sleeps (no billing) | Keep-warm only during active hours (cron window) to be a good citizen |
| Postgres | Neon free | 0.5 GB, compute-hours cap | Suspends (no billing) | TTL sweeps on cache/jobs tables; size alert at 70% via weekly job |
| Object storage | Cloudflare R2 | 10 GB, 1M class-A/10M class-B ops/mo | **Requires card? No — R2 free tier needs a Cloudflare account; verify no-card status at setup** `[VERIFY]`; ops overage would bill if card attached → keep no card / zero-spend guard | Per-user storage report; upload caps; thumbnail sizes |
| LLM API | Groq-class free tier | RPM/RPD caps | 429s (no billing) | Per-user assistant quotas (API_DESIGN); deterministic fallback (D20) |
| USDA FDC | free key | 1k req/hr | 429s | Cache-first + seeded mappings |
| OFF | free | polite use | n/a | Cache + UA identification |
| Email | Brevo/Resend-class free | ~100–300/day | Hard stop | Transactional only; verify at pick `[VERIFY]` |
| W&B | free | 100 GB artifacts | Upload fails | Rolling checkpoint cleanup (TRAINING_PLAN) |
| GPU training | Kaggle/Colab free | ~30 h/wk | Session ends | EXPERIMENT_PLAN sequencing; checkpoints |
| CI | GitHub Actions free (public repo) | Unlimited public-repo minutes (fair use) | Throttle | Cache deps; path filters |
| GHCR / git-lfs | free tiers | LFS 1 GB/mo bandwidth | Blocks | Keep fixtures small; large fixtures generated not stored |

## Rules

1. **Never attach a payment method** to beta-serving accounts where the provider
   bills overage automatically; prefer providers that throttle instead.
2. Any new dependency requires a row in this table before adoption (checked in PR
   review).
3. Quota telemetry: weekly job posts usage summary (DB size, R2 usage, LLM 429 rate,
   FDC hit rate) to the admin endpoint + log (OBSERVABILITY).
4. Degradation ladder is designed, not accidental: LLM→fallback summary; FDC→cache;
   OFF→cache/absent; Space asleep→waking banner. The app stays honest and usable
   through every quota cliff.

## If budget ever appears

Priority order for first dollars: 1) container host that doesn't sleep (~$7–20/mo)
— kills cold starts, the single biggest UX cost; 2) Apple dev account ($99/yr) for
TestFlight; 3) AWS migration per AWS_ARCHITECTURE (~$40–70/mo estimate
`[VERIFY AT MIGRATION]`).
