"""Telemetry session loading and resampling.

Loads an RTE runtime-session JSONL export into per-signal (t, v) arrays
and provides nearest / median-window resampling onto an arbitrary time
grid. All channels are cleaned (non-finite dropped, optional validity
predicate, optional abs clamp) before use.

Session paths may point at the plain .jsonl export or at a compressed
copy: .jsonl.gz (gzip streaming) and .jsonl.zst (decompressed through
the `zstd` CLI, since the repo policy stores raw sessions as
`zstd -19 --long=31` output). Everything is streamed line by line;
no file is ever read fully into memory.
"""
import gzip
import io
import json
import subprocess

import numpy as np


def _open_session(path):
    """Return a streaming text reader for a .jsonl / .jsonl.gz / .jsonl.zst
    session file. The returned context manager yields a line iterator.

    For .zst the `zstd` CLI must be on PATH; the stream is piped through
    `zstd -dc --long=31` (the --long window the repo archive policy uses).
    Raises a clear RuntimeError if the CLI is missing or decompression
    fails (corrupt file, unsupported window, ...).
    """
    path = str(path)
    if path.endswith(".zst"):
        try:
            proc = subprocess.Popen(
                ["zstd", "-dc", "--long=31", "--", path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except OSError as exc:
            raise RuntimeError(
                f"cannot read {path}: the `zstd` CLI is required to "
                f"decompress .zst sessions but could not be executed ({exc})"
            ) from exc

        proc_err = None

        class _ZstdStream:
            def __enter__(self):
                fh = io.TextIOWrapper(proc.stdout, encoding="utf-8")
                self._fh = fh
                return fh

            def __exit__(self, exc_type, exc, tb):
                nonlocal proc_err
                try:
                    self._fh.close()
                except BrokenPipeError:
                    pass
                finally:
                    if proc.stdout is not None and not proc.stdout.closed:
                        proc.stdout.close()
                    proc_err = proc.stderr.read().decode(
                        "utf-8", "replace").strip()
                    code = proc.wait()
                    proc.stderr.close()
                if exc_type is None and code != 0:
                    raise RuntimeError(
                        f"zstd failed to decompress {path} "
                        f"(exit {code}): {proc_err or 'no stderr output'}. "
                        f"The file may be corrupt or use a --long window "
                        f"unsupported by this zstd build."
                    )
                return False

        return _ZstdStream()

    if path.endswith(".gz"):
        gz = gzip.open(path, "rb")
        reader = io.TextIOWrapper(gz, encoding="utf-8")

        class _GzipStream:
            def __enter__(self):
                return reader

            def __exit__(self, exc_type, exc, tb):
                reader.close()
                # Mid-stream gzip corruption surfaces during iteration
                # (BadGzipFile / EOFError), not on close.
                if exc_type is not None and isinstance(
                        exc, (gzip.BadGzipFile, EOFError)):
                    raise RuntimeError(
                        f"gzip failed to decompress {path}: {exc}. "
                        f"The file may be corrupt.") from exc
                return False

        return _GzipStream()

    return open(path, encoding="utf-8")


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
        with _open_session(path) as fh:
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
