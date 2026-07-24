# OCR Architecture

## Engine comparison

| Engine | Accuracy on packaging | Mobile | Cost | Latency (CPU) | Offline | Privacy | Tables | Rotation/curve tolerance | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **PaddleOCR (PP-OCRv4/v5)** | Strong on scene/product text; det+rec+angle pipeline | Server-side (mobile ports exist but heavy) | Free (Apache-2.0) | ~0.5–2 s/image CPU | Yes (self-host) | Full (our infra) | Layout modules available | Good (detects rotated text lines) | **MVP choice** |
| Tesseract 5 | Weak on curved/stylized/low-contrast packaging; strong on clean documents | Poor fit | Free (Apache-2.0) | Fast on clean text | Yes | Full | Basic | Poor without heavy preprocessing | Fallback comparison only; documented honestly |
| EasyOCR | Decent scene text; slower; heavier | No | Free | Slow CPU | Yes | Full | No | Moderate | No advantage over Paddle for us |
| Google ML Kit (on-device) | Very good; free | **Yes (native)** | Free | Fast on-device | Yes | Excellent (never leaves device) | No | Good | **Later offline/on-device option (R5, dev-build)**; not in Expo Go |
| AWS Textract | Excellent forms/tables | No | **Paid** | API | No | Third party | Excellent | Good | Violates D0; noted as the "cloud-accuracy option" we deliberately rejected |
| Google Cloud Vision | Excellent | No | Paid beyond trivial free quota | API | No | Third party | Good | Good | Same rejection |
| Apple Vision (platform) | Very good | iOS only | Free | Fast | Yes | Excellent | No | Good | iOS-only splits behavior; possible R5 per-platform path |

## Recommendations

- **MVP:** PaddleOCR server-side in the API container. One engine, one behavior for
  all users, testable in CI, zero cost, no data leaves our infra.
- **Privacy-first option:** ML Kit on-device (R5, requires dev builds — D7 allows).
- **Cloud-accuracy option:** Textract/Cloud Vision — documented, rejected under D0;
  the interface (`OcrEngine` protocol) keeps the slot open.
- **Offline option:** ML Kit (same as privacy-first).

Engine sits behind `OcrEngine` protocol: `run(image) -> OcrResult{lines[], tokens[],
boxes[], confidences[], engine_version}` so engines are swappable and results
comparable on fixtures.

## Pipeline stages (server)

1. **Image-quality check** — reuse deterministic quality module (blur/exposure/
   resolution). Low quality → proceed but tag result; UI suggests retake
   (SAFETY_MODEL: never hard-block).
2. **Document/label detection** — locate the label region: contour + edge heuristics
   first (deterministic); if insufficient on fixtures, PaddleOCR's detection output
   bounding region is used directly. No trained detector of our own for MVP.
3. **Perspective correction** — homography from detected quadrilateral when confident;
   skipped (with flag) when quad detection is ambiguous — a wrong warp is worse than
   none.
4. **Rotation correction** — PaddleOCR angle classifier + coarse 90° orientation fix
   from EXIF/heuristic.
5. **Contrast enhancement** — CLAHE + adaptive denoise, parameters fixed by fixture
   tuning; applied copy only (original preserved).
6. **OCR** — PaddleOCR det+rec with per-token confidences.
7. **Layout parsing** — group tokens → lines → blocks by geometry; reading order
   resolution (multi-column tolerated).
8. **Section detection** — classify blocks: ingredient list / allergen statement /
   nutrition panel / other, via keyword anchors ("INGREDIENTS:", "Contains", "Nutrition
   Facts", "% Daily Value") + layout position. Deterministic rules; fixture-tested.
9. **Field extraction** — mode-specific parsers (INGREDIENT_EXTRACTION,
   NUTRITION_LABEL_EXTRACTION).
10. **Confidence scoring** — per-token (engine), per-field (aggregation), and
    **completeness estimate**: readable-text area ÷ detected-text-region area, plus
    low-confidence-token ratio. Drives the completeness indicator and the
    NOT_FOUND→INSUFFICIENT demotion (SAFETY_MODEL).
11. **User correction** — every extracted field editable in-app; corrections re-run
    stages 8–10 downstream; correction events stored (D16 consent governs training
    reuse).

## Performance posture

OCR runs async (ASYNC_JOB_DESIGN); budget p95 ≤ 6 s server-side per label image on
free-tier CPU (PERFORMANCE_BUDGET). PaddleOCR "mobile/slim" detection+recognition
model variants are the default; "server" variants only if fixture accuracy demands
and latency budget survives — decided by measurement.

## Failure behavior

Engine crash/timeout → scan enters `ocr_failed` state with retry affordance; no
partial results presented as complete; allergen statuses for the scan become
`INSUFFICIENT` (never `NOT_FOUND`).
