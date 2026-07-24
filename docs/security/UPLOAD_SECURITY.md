# Upload Security

Untrusted bytes → validated canonical image. Complements IMAGE_LIFECYCLE.

- **Allowed types:** JPEG, PNG, WebP, HEIC (mobile reality). Detection by **file
  signature (magic bytes)**, never extension or client MIME. Content sniffing
  disabled on any serving path (`X-Content-Type-Options: nosniff`).
- **Size limits:** presign policy caps 8 MB; API multipart cap 8 MB; reject before
  buffering (streaming check).
- **Pixel limits:** decode bomb guard — bounds check from header pre-decode where
  possible; Pillow `MAX_IMAGE_PIXELS = 25_000_000`; dimension bounds 128–8000 px per
  side.
- **Decode isolation:** decode + re-encode in a resource-limited **subprocess**
  (rlimits: CPU 10 s, RSS 512 MB, no network); crash → reject. Image libs pinned +
  vulnerability-scanned (CI).
- **Canonicalization:** always re-encode to baseline JPEG (sRGB, q90) — strips
  metadata (EXIF/GPS), neutralizes polyglots/appended payloads, normalizes HEIC.
  Original bytes are **not** retained (canonical file is the stored original).
- **Metadata handling:** orientation applied, then all metadata dropped; CI fixture
  test asserts GPS-tagged upload → stored object metadata-free (IMAGE_LIFECYCLE).
- **Storage permissions:** private bucket; service credentials scoped to the two
  prefixes; presigned PUTs constrain content-length-range and key (server-chosen
  UUID key — user filenames never reach storage).
- **Serving:** signed GET only (15 min), ownership-checked mint; no direct bucket
  exposure.
- **Malware scanning:** ClamAV considered — poor value for images that are
  immediately re-encoded and never executed/redistributed; **decision: rely on
  canonicalization instead** (recorded; revisit if user-to-user sharing ever ships).
- **Rate limits:** 30 uploads/hr/user (API_DESIGN); per-IP caps on presign;
  upload-abuse metrics + alerting (repeated rejects → flag account)
  (OBSERVABILITY).
- **Abuse monitoring:** rejected-upload counter per user/IP; threshold alert;
  storage-usage-per-user report guards free-tier quota (COST_MODEL).
