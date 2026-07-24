# Offline & Edge Behavior

MVP is cloud-inference (D15): honest offline states beat fake capability.

## Capability matrix

| Capability | Fully on-device | From cache | Online only |
|---|---|---|---|
| Camera capture + quality hints | ✅ | — | — |
| Barcode **detection** | ✅ (expo-camera) | — | — |
| Barcode product **lookup** | — | ✅ previously-scanned products (Query cache) | ✅ new products |
| Food classification | ❌ MVP (R5: quantized on-device) | — | ✅ |
| OCR + parsing + allergen evidence | ❌ MVP | ✅ previously-completed scans re-viewable | ✅ |
| Nutrition values | — | ✅ viewed scans | ✅ new lookups |
| Dietary profile view/edit | edit queues | ✅ | sync |
| Scan history | — | ✅ last 50 cached | ✅ full |
| Assistant | ❌ | ❌ (threads viewable read-only) | ✅ |
| Export/deletion | ❌ | — | ✅ |

## Offline behaviors

- **Global offline chip** when connectivity lost; cached screens render with "as of
  <time>" staleness note.
- **Capture queue:** up to 5 captured scans stored locally (image + mode + draft
  metadata) with "waiting for connection" state; auto-upload on reconnect
  (foreground); queue visible in history as pending items.
- **No degraded analysis:** the app never runs a weaker local guess in MVP — a
  pending scan is pending, not approximated.
- **Profile edits offline:** optimistic local change + sync-on-reconnect with
  conflict rule server-wins + notify (rare at single-user scale).
- **Auth:** cached session works offline for cached views; actions requiring fresh
  tokens fail gracefully to the offline state.

## Free-tier cold start (edge-adjacent reality)

Backend may sleep (STORAGE_STRATEGY). First request path: `/healthz` ping on app
foreground; if slow → "waking up the scanner (~30 s)" banner preemptively on Home,
so the first scan doesn't feel broken.

## R5 on-device path (designed now, built later)

Distilled+quantized student (E15/E16) via ONNX Runtime Mobile in a dev-build;
on-device results marked as such in provenance (`model_location: device`), same
confirmation UX and thresholds (recalibrated per model); label OCR on-device via
ML Kit as the R5 privacy option. The scan API already records model provenance per
event, so hybrid provenance requires no schema change.
