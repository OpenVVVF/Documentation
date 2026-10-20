# OpenVVVF Test Registry

`Data/Tests/` is the **bulk-evidence store** for tests. **It never
competes with the docs tree for identity.** One test has one identity:
its integer `test_id` and its slug, both defined in the frontmatter of
the test report under `Docs/Testing/`.

## Where things live

| What | Path | Tracked? |
|------|------|----------|
| Test plan / report (Index.md) | `Docs/Testing/<Domain>/<Slug>/` | yes |
| Reviewable small evidence (decimated telemetry, figures, photos) | `Docs/Testing/<Domain>/<Slug>/` | yes |
| Bulk raw evidence (full session exports) | `Data/Tests/<DOM>-<Slug>/raw/` | **yes, if compressed** (see below) |
| Videos (source camera files) | `Data/Tests/<DOM>-<Slug>/raw/` | untracked (too big) |
| Rendered overlays and other derived output | `Data/Tests/<DOM>-<Slug>/video/` | untracked |
| Test manifest | `Data/Tests/index.json` | **generated — do not hand-edit** |

### Compression policy for raw telemetry

RTE runtime-session JSONL compresses ~10× (gzip) to ~17× (zstd -19).
Commit raw captures as `*.jsonl.zst`:

```sh
zstd -19 --long=31 -T 8 session.jsonl && rm session.jsonl
```

The browser telemetry viewer (`Docs/Tools/OpenVVVF-Telemetry-Viewer`)
opens `.jsonl`, `.jsonl.gz`, and `.jsonl.zst` directly — decompression
happens in the browser, no server or local unpack needed. Committing a
1.5 GB session costs ~90 MB of git history this way. Videos are NOT
compressible and stay untracked.

`<DOM>` is the domain prefix used by the report's `doc_id`:
`HW` (Hardware), `FW` (Firmware), `INT` (Integration). The data folder
name therefore mirrors the report folder mechanically, e.g.

```text
Docs/Testing/Integration/Zero-DSR-Road-Test/          # report + small evidence
Data/Tests/INT-Zero-DSR-Road-Test/raw/                # full session export (untracked)
```

## Workflow

1. New test → next free integer `test_id` (see the dashboard in
   `Docs/Testing/Index.md`), report folder under the matching domain,
   frontmatter with `doc_id: OV-TEST-<DOM>-<SLUG-TAIL>`.
2. Bulk evidence → mirrored `Data/Tests/<DOM>-<Slug>/raw/`. Never
   commit large exports to the repo; decimated versions go next to the
   report instead.
3. Regenerate the manifest: `python3 Data/Tests/rebuild_index.py`.
   It validates unique test IDs and correct mirroring, and rewrites
   `index.json` from the doc frontmatter. `python -m docgen validate`
   covers the doc tree itself.

## Branding note

Videos from `Tools/TelemetryOverlay` brand themselves from the same
identity: the intro/outro and watermark read the test number/title
from the run config, which must match the registered `test_id`.
