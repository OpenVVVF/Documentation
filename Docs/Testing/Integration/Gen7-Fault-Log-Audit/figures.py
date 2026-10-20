#!/usr/bin/env python3
"""Render fig-01 for the Gen7 fault-log audit report.

Streams the zstd-compressed raw session (via `zstd -dc --long=31`,
same idiom as parse_fault_log.py), re-extracts the 29 unique fault-log
records, and draws the fault-log timeline structured by boot: record
position within the boot (log ms) on the y-axis, boot number on the
x-axis, colour by fault source, filled/open marker by severity.
"""
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RAW = (HERE.parents[3] / "Data" / "Tests" / "INT-Gen7-Fault-Log-Audit" /
       "raw" / "runtime-session-2026-10-19T10-56-50.375Z-17521eb9.jsonl.zst")

STYLE = {
    "CanErrorPassive": ("tab:blue", "FDCAN error-passive"),
    "CoprocessorSafety": ("tab:red", "coprocessor-safety latch"),
    "PhaseOvercurrent": ("tab:orange", "phase overcurrent"),
    "DcLinkCurrentFeedback": ("tab:purple", "DC-link feedback"),
    "RamEcc": ("tab:green", "RAM ECC"),
}


def load_records(path):
    proc = subprocess.Popen(["zstd", "-dcq", "--long=31", str(path)],
                            stdout=subprocess.PIPE)
    by_seq = {}
    for line in proc.stdout:
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") == "state" and o.get("signal") == "fault_log_record":
            kv = dict(tok.split("=", 1) for tok in o.get("value", "").split()
                      if "=" in tok)
            by_seq[kv.get("seq")] = (
                int(kv["boot"]), float(kv["ms"]) / 1000.0,
                kv.get("source", "?"), int(kv.get("severity", "0")))
    return by_seq.values()


def main():
    recs = load_records(RAW)
    jitter = {src: (i - 2) * 0.07 for i, src in enumerate(STYLE)}
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    seen = set()
    for boot, s, src, sev in recs:
        color, label = STYLE.get(src, ("tab:gray", src))
        x = boot + jitter.get(src, 0.14)
        ax.scatter(x, s, s=55 if sev else 30,
                   edgecolors=color, facecolors=color if sev else "none",
                   linewidths=1.4, alpha=0.9,
                   label=label if src not in seen else None)
        seen.add(src)
    ax.set_yscale("log")
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("boot number (log has no calendar timestamps)")
    ax.set_ylabel("time within boot [s, log scale]")
    ax.set_title("Persisted fault log — 29 records by boot and in-boot time "
                 "(filled = severity 2, open = severity 0)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    fig.tight_layout()
    out = HERE / "fig-01-fault-log-timeline.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
