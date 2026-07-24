# Image Lifecycle

From capture to deletion. Security gates detailed in UPLOAD_SECURITY; this doc is the
pipeline and retention view.

## 1. Upload

Preferred: `POST /v1/images/presign` → short-lived (5 min) pre-signed PUT to object
storage (size-capped via signed policy) → `POST /v1/images/complete` triggers
server-side validation job. Fallback: direct multipart to API (small images).
Client downscales before upload (CAMERA_UX: longest side 1600 px, JPEG q85 — plenty
for 224–384 px models and OCR while cutting upload time ~10×).

## 2. Validation (server, before any processing)

Magic-byte signature check (JPEG/PNG/WebP/HEIC allowlist) → decode in a
resource-limited subprocess (Pillow with `MAX_IMAGE_PIXELS` cap 25 MP —
decompression-bomb guard) → dimension/size bounds → re-encode to canonical JPEG
(kills polyglot/steganographic payload concerns and normalizes HEIC). Failure →
object deleted immediately, image record marked rejected, user gets clear error.

## 3. Metadata removal

EXIF/XMP/IPTC stripped during canonical re-encode — **GPS never persists**.
Orientation applied before stripping. `exif_stripped=true` recorded; a CI test
uploads a GPS-tagged fixture and asserts the stored object is clean.

## 4. Object naming & layout

`images/{user_id}/{image_id}.jpg` + `thumbs/{user_id}/{image_id}.jpg` (320 px).
UUIDv7 ids — **no user-supplied filenames touch storage keys**. Bucket is private;
no public ACLs; browser/app access via time-limited signed GETs (15 min) minted
per-request after ownership check (no capability-URL reuse across users).

## 5. Encryption

TLS in transit; at rest via provider (R2 encrypts by default; SSE-S3 in the AWS
design). Client-side encryption assessed and rejected for MVP (key management burden
vs threat model for food photos; recorded in THREAT_MODEL).

## 6. Processing access

Pipeline stages read via internal storage client (service credentials scoped to the
bucket); no signed-URL indirection internally.

## 7. Retention & deletion (D21)

- Default: keep until user deletes.
- Scan soft-delete → 7-day grace (undo) → hard sweep deletes original + thumbnail +
  derived OCR text? — **no**: OCR text is part of the scan graph and deletes with
  the scan rows; the sweep covers storage objects and DB graph together.
- Account deletion: enumerated deletion of `images/{user_id}/*` + `thumbs/…` +
  export archives, verified by post-sweep listing (empty prefix assertion) recorded
  in the audit trail.
- Orphan sweep: weekly job reconciles storage-prefix listings vs DB records both
  directions (storage-without-row → delete; row-without-object → mark broken).

## 8. Access logs

API-level access to signed-URL minting is logged (user, image, purpose). Provider
object logs are out of scope on free tier (documented gap; AWS design adds S3 access
logs).

## 9. Training-data opt-in path (D16)

Only for `training_images` consent: at dataset-build time (R5), consented scans'
images are **copied** into a separate `training-staging/` prefix with a manifest
(scan id, consent version, copy date); originals' lifecycle stays user-controlled;
revocation excludes from future builds (already-trained models disclosed at opt-in,
J11). Review queue before anything enters a dataset (FEEDBACK_LOOP).
