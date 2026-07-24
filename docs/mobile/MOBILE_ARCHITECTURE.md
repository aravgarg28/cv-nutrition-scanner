# Mobile Architecture

Expo (React Native, TypeScript). Distribution: Expo Go during development, EAS
development builds for anything Expo Go can't host (D7). Target: iOS + Android from
one codebase.

## Stack decisions

| Concern | Choice | Rationale |
|---|---|---|
| Framework | Expo SDK (managed workflow) | D7; free EAS tier covers dev builds |
| Navigation | Expo Router (file-based, typed routes) | Standard, deep-linkable |
| Server state | TanStack Query | Polling, cache, retry, offline-tolerant reads — most app state is server state |
| Client state | Zustand (small stores: auth session, active profile, capture draft) | Minimal; avoid Redux ceremony |
| Networking | fetch wrapper + generated TS client from OpenAPI (shared-schemas) | Single source of truth for types |
| Auth storage | expo-secure-store (Keychain/Keystore) for refresh token; access token in memory | SECURITY: no tokens in AsyncStorage |
| Camera | expo-camera (photo + barcode scanning) | Covers modes incl. barcode (D13) without dev-build |
| Image ops | expo-image-manipulator (downscale/compress pre-upload) | IMAGE_LIFECYCLE client contract |
| Forms/validation | zod schemas shared conceptually with backend enums | Status codes/enums generated, never retyped |
| Analytics | **None** (D1 beta privacy) | In-app feedback widget only |
| Error reporting | Sentry **not** included in beta (privacy review first); dev-menu log export instead | PRIVACY_MODEL |

## App structure

```
apps/mobile/src/
  app/            # expo-router routes (auth)/(tabs)/scan, history, profile, settings
  features/       # capture, scan-results, allergen-evidence, assistant, history,
                  # profile, onboarding — screen logic + components per feature
  api/            # generated client + query hooks (useScan, useConfirmScan…)
  stores/         # zustand stores
  ui/             # design-system components: TypedFact, StatusRow (ALLERGEN_POLICY
                  # renderers), ConfidenceBar, SourceChip, Disclaimer
  lib/            # upload pipeline, image utils, polling helpers
```

The **StatusRow / TypedFact components are the safety-critical UI kernel**: they are
the only way allergen statuses and typed information render; snapshot + literal-string
tests pin their copy to ALLERGEN_POLICY (no screen builds its own allergen text).

## Key flows

- **Auth:** refresh-token rotation handled in the fetch wrapper (401 → refresh →
  retry once → logout on failure); session store drives route guards.
- **Capture → upload:** capture/gallery → client downscale → presigned PUT with
  progress → `POST /scans` → navigate to processing screen.
- **Scan polling:** TanStack Query `refetchInterval` driven by scan state (1 s while
  processing, stop on terminal states, `Retry-After` respected); processing screen
  renders stage messages from state enum.
- **Background behavior:** uploads continue via retry-on-foreground (no background
  task in Expo Go); a scan interrupted by app kill resumes from server state (scan
  id persisted in capture draft store).
- **Offline (OFFLINE_AND_EDGE):** reads from Query cache flagged stale; captures
  queue locally (max 5) and upload on reconnect; all analysis requires connectivity —
  honest "offline" states, no fake results.
- **Deep links:** `snapnutrition://scan/{id}` for history entries (and future share).

## Error handling

Central error mapper: API error codes → user copy (shared enum); network errors →
retry affordances; scan `*_failed` states → per-stage retry buttons. No raw error
strings from server surfaces to users (they may embed provider text).

## Accessibility

Per HUMAN_FACTORS: dynamic type, screen-reader labels on StatusRow (composed
sentence), 44 pt targets, CVD-safe status styling (icon+text+color), reduced-motion
respect. Accessibility props are part of component acceptance criteria, not a
post-pass.

## Testing

Component tests (React Native Testing Library) for the safety kernel + flows;
mocked-API integration tests for auth/scan/confirm; Maestro E2E happy-path suite on
CI (Android emulator) for J4→J8; manual device matrix before releases
(TEST_STRATEGY).
