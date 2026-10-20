#!/usr/bin/env python3
"""Parse the Gen7 persisted fault log from an RTE runtime-session export.

Streams the zstd-compressed raw session via ``zstd -dc --long=31``
(no zstandard wheel in the repo venv, same idiom as test 12's
``figures.py``) — or a plain ``.jsonl`` — and extracts
the board's persisted fault log as replayed through the TLM1 signals:

- ``fault_log_record``  state lines, one per persisted record
- ``fault_log_latest``  state line, the newest record
- ``fault_log_count``   telemetry line, number of records retained

Prints one row per record (seq, boot, on-boot ms, source/reason, severity,
and the decoded detail fields) plus a summary of boots, sources, and
severities. All key/value parsing is pass-through: fields with unknown
semantics are printed raw, never interpreted.

Usage:
    python3 parse_fault_log.py [session.jsonl[.zst]]
"""
import gzip
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SESSION = (
    HERE.parents[3] / "Data" / "Tests" / "INT-Gen7-Fault-Log-Audit" / "raw"
    / "runtime-session-2026-10-19T10-56-50.375Z-17521eb9.jsonl.zst"
)


def open_session(path):
    name = path.name
    if name.endswith(".zst"):
        proc = subprocess.Popen(
            ["zstd", "-dcq", "--long=31", str(path)],
            stdout=subprocess.PIPE)
        return proc.stdout
    if name.endswith(".gz"):
        return gzip.open(path, "rb")
    return path.open("rb")


def parse_kv(value):
    kv = {}
    for tok in value.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def detail(rec):
    """Structurally obvious per-source detail; unknown fields stay raw."""
    kv = rec["kv"]
    fields = kv.get("fields", "").split(",")
    values = kv.get("values", "").split(",")
    fv = dict(zip(fields, values)) if kv.get("values") else {}
    src = kv.get("source", "")
    out = []
    if src == "CanErrorPassive":
        out.append(f"psr={fv.get('psr', '?')} ecr={fv.get('ecr', '?')} "
                   f"(raw FDCAN PSR/ECR register snapshots)")
    elif src == "CoprocessorSafety":
        out.append(f"generation=0x{fv.get('generation', '?')} "
                   f"age_ms=0x{fv.get('age_ms', '?')} "
                   f"trip_reason=0x{fv.get('trip_reason', '?')} "
                   f"trip_inputs=0x{fv.get('trip_inputs', '?')}")
    elif src == "PhaseOvercurrent":
        cur = {k: float(fv[k]) for k in
               ("iu_a", "iv_a", "iw_a", "iq_a", "id_a") if k in fv}
        lim = float(fv["limit_a"]) if "limit_a" in fv else None
        out.append(" ".join(f"{k[:-2]}={v:.2f}A" for k, v in cur.items())
                   + (f" limit={lim:.0f}A" if lim is not None else ""))
    elif src == "DcLinkCurrentFeedback":
        cur_a = float(fv["current_a"]) if "current_a" in fv else None
        bits = ", ".join(f"{k}={fv[k]}" for k in
                         ("age_ms", "calibrated", "valid", "iq_a",
                          "iq_request_a") if k in fv)
        out.append((f"current={cur_a:.3f}A " if cur_a is not None else "")
                   + bits)
    else:
        out.append(" ".join(f"{k}={v}" for k, v in fv.items()))
    # gate/bdtr/ccer are structurally uniform but semantically unknown:
    # print raw so a reviewer sees them without invented meaning.
    out.append(f"bdtr={kv.get('bdtr', '?')} ccer={kv.get('ccer', '?')} "
               f"gate={kv.get('gate', '?')}")
    return f"kind={kv.get('kind', '?')} " + (out[0] if out else "")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SESSION
    records, latest, counts = [], None, []
    state_samples = 0
    with open_session(path) as fh:
        for line in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "state":
                sig = obj.get("signal")
                if sig == "fault_log_record":
                    records.append({"t": obj.get("t"),
                                    "kv": parse_kv(obj.get("value", ""))})
                    state_samples += 1
                elif sig == "fault_log_latest":
                    latest = parse_kv(obj.get("value", ""))
            elif obj.get("type") == "telemetry":
                vals = obj.get("values", {})
                if "fault_log_count" in vals:
                    counts.append((obj.get("t"), vals["fault_log_count"]))

    seen_seqs = Counter()
    for r in records:
        seen_seqs[r["kv"].get("seq", "?")] += 1
    unique = list({r["kv"].get("seq", "?"): r for r in records}.values())
    unique.sort(key=lambda r: int(r["kv"].get("seq", "0")))

    print(f"session: {path.name}")
    print(f"state samples of fault_log_record: {state_samples} "
          f"(unique seqs: {len(unique)})")
    if counts:
        vals = [c for _, c in counts]
        print(f"fault_log_count: {vals[0]:.0f} -> {vals[-1]:.0f} "
              f"over {len(vals)} samples (never changed live: "
              f"{len(set(vals)) == 1})")
    if latest:
        print(f"fault_log_latest: seq={latest.get('seq')} boot={latest.get('boot')} "
              f"ms={latest.get('ms')} source={latest.get('source')} "
              f"severity={latest.get('severity')}")
    print()
    hdr = f"{'seq':>3} {'boot':>4} {'ms':>9} {'sev':>3} {'source':<24} reason / detail"
    print(hdr)
    print("-" * len(hdr))
    boots = Counter()
    sources = Counter()
    sevs = Counter()
    by_boot = defaultdict(set)
    for r in unique:
        kv = r["kv"]
        boots[kv.get("boot", "?")] += 1
        sources[kv.get("source", "?")] += 1
        sevs[kv.get("severity", "?")] += 1
        by_boot[kv.get("boot", "?")].add(kv.get("source", "?"))
        print(f"{kv.get('seq','?'):>3} {kv.get('boot','?'):>4} "
              f"{kv.get('ms','?'):>9} {kv.get('severity','?'):>3} "
              f"{kv.get('source','?'):<24} {kv.get('reason','?')} | {detail(r)}")
    print()
    print(f"boots represented: {len(boots)} -> "
          + ", ".join(f"boot {b}: {n} rec" for b, n in sorted(boots.items(), key=lambda x: int(x[0]))))
    print("sources: " + ", ".join(f"{s} x{n}" for s, n in sources.most_common()))
    print("severities: " + ", ".join(f"sev {s}: {n}" for s, n in sevs.items()))
    dup = {s: n for s, n in seen_seqs.items() if n > 1}
    if dup:
        print("duplicate seq replay samples: "
              + ", ".join(f"seq {s} x{n}" for s, n in sorted(dup.items(), key=lambda x: int(x[0]))))
    print()
    print("sources per boot:")
    for b in sorted(by_boot, key=lambda x: int(x)):
        print(f"  boot {b}: {', '.join(sorted(by_boot[b]))}")


if __name__ == "__main__":
    main()
