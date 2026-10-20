"""Telemetry session loading and resampling.

Loads an RTE runtime-session JSONL export into per-signal (t, v) arrays
and provides nearest / median-window resampling onto an arbitrary time
grid. All channels are cleaned (non-finite dropped, optional validity
predicate, optional abs clamp) before use.
"""
import json

import numpy as np


class Session:
    def __init__(self, path):
        self.path = path
        self.signals = {}  # name -> (t ndarray, v ndarray), cleaned
        self.started_at_utc = None
        self.duration = 0.0
        self._load(path)

    def _load(self, path):
        raw = {}
        started = None
        last_t = 0.0
        with open(path) as fh:
            for line in fh:
                d = json.loads(line)
                ty = d.get("type")
                if ty == "session_start":
                    started = d.get("started_at_utc")
                elif ty == "telemetry":
                    t = d["t"]
                    last_t = max(last_t, t)
                    for k, v in d["values"].items():
                        if v is None:
                            continue
                        raw.setdefault(k, []).append((t, v))
        self.started_at_utc = started
        self.duration = last_t
        for k, pts in raw.items():
            a = np.asarray(pts, dtype=float)
            m = np.isfinite(a[:, 1])
            self.signals[k] = (a[m, 0], a[m, 1])

    def names(self):
        return sorted(self.signals)

    def has(self, name):
        return name in self.signals and len(self.signals[name][0]) > 0

    def cleaned(self, name, max_abs=None, valid=None):
        t, v = self.signals[name]
        if valid is not None:
            m = valid(v)
            t, v = t[m], v[m]
        if max_abs is not None:
            m = np.abs(v) <= max_abs
            t, v = t[m], v[m]
        return t, v

    @staticmethod
    def resample_nearest(tv, grid):
        """Value of the closest sample to each grid point."""
        t, v = tv
        if len(t) == 0:
            return np.zeros(len(grid))
        idx = np.clip(np.searchsorted(t, grid), 1, len(t) - 1)
        left = np.abs(grid - t[idx - 1]) <= np.abs(grid - t[idx])
        return np.where(left, v[idx - 1], v[idx])

    @staticmethod
    def resample_median(tv, grid, win=0.15):
        """Median of samples within +-win of each grid point (glitch-proof)."""
        t, v = tv
        lo = np.searchsorted(t, grid - win)
        hi = np.searchsorted(t, grid + win)
        out = np.empty(len(grid))
        for i in range(len(grid)):
            if hi[i] > lo[i]:
                out[i] = np.median(v[lo[i]:hi[i]])
            elif hi[i] > 0:
                out[i] = v[hi[i] - 1]
            else:
                out[i] = v[0] if len(v) else 0.0
        return out
