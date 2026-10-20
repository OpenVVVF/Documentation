import numpy as np
import pytest

from telemetry_overlay.telemetry import Session


def _assert_same_signals(a, b):
    assert a.names() == b.names()
    assert a.started_at_utc == b.started_at_utc
    np.testing.assert_allclose(a.duration, b.duration)
    for name in a.names():
        ta, va = a.signals[name]
        tb, vb = b.signals[name]
        assert len(ta) == len(tb)
        np.testing.assert_allclose(ta, tb, rtol=0, atol=1e-12)
        np.testing.assert_allclose(va, vb, rtol=1e-9, atol=1e-12)


def test_load(session_file):
    s = Session(session_file)
    assert s.started_at_utc == "2026-10-16T18:17:05Z"
    assert s.duration == 4.0
    # None values are dropped per-row; non-finite values are cleaned
    assert s.has("thr_a_norm") and s.has("display_speed_mph")
    vt, vv = s.signals["thr_a_norm"]
    assert list(vt) == [0.0, 1.0, 3.0, 4.0]  # NaN row dropped
    assert np.all(np.isfinite(vv))
    mt, mv = s.signals["display_speed_mph"]
    assert list(mt) == [0.0, 1.0, 2.0, 4.0]  # inf row dropped
    # signal_definition lines are ignored (not signals)
    assert "signal_definition" not in s.names()


def test_cleaned(session_file):
    s = Session(session_file)
    t, v = s.cleaned("cg_iq_a", max_abs=60)
    assert list(v) == [40.0, 0.0, 55.0]  # |-90| out of range -> dropped
    t, v = s.cleaned("thr_a_norm", valid=lambda v: v > 0.1)
    assert list(v) == [0.5, 1.0, 0.8]


def test_resample_nearest():
    t = np.array([0.0, 1.0, 2.0, 4.0])
    v = np.array([10.0, 20.0, 30.0, 50.0])
    grid = np.array([0.4, 0.6, 3.1, 10.0, -5.0])
    out = Session.resample_nearest((t, v), grid)
    np.testing.assert_array_equal(out, [10.0, 20.0, 50.0, 50.0, 10.0])


def test_resample_median_glitch():
    # a single-sample glitch inside the window must not change the median
    t = np.linspace(0, 4, 21)
    v = np.zeros(21)
    v[10] = 900.0
    grid = np.array([2.0])
    out = Session.resample_median((t, v), grid, win=0.3)
    assert out[0] == 0.0


def test_resample_empty():
    grid = np.array([0.0, 1.0])
    out = Session.resample_nearest((np.array([]), np.array([])), grid)
    np.testing.assert_array_equal(out, [0.0, 0.0])


def test_load_gzip(session_file, tmp_path):
    import gzip

    gz_path = tmp_path / "session.jsonl.gz"
    with gz_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb") as gz:
            gz.write(session_file.read_bytes())
    s_gz = Session(gz_path)
    s_plain = Session(session_file)
    _assert_same_signals(s_gz, s_plain)
    # spot-check per-signal count / first / last
    tg, vg = s_gz.signals["display_speed_mph"]
    assert len(vg) == 4
    np.testing.assert_allclose([vg[0], vg[-1]], [0.0, 31.0])


def test_load_zstd(session_file, tmp_path):
    import shutil
    import subprocess

    if shutil.which("zstd") is None:
        pytest.skip("zstd CLI not on PATH")
    zst_path = tmp_path / "session.jsonl.zst"
    with zst_path.open("wb") as out:
        res = subprocess.run(
            ["zstd", "-19", "--long=31", "-c", "--", str(session_file)],
            stdout=out, stderr=subprocess.PIPE)
        assert res.returncode == 0, res.stderr
    s_zst = Session(zst_path)
    s_plain = Session(session_file)
    _assert_same_signals(s_zst, s_plain)
    tt, vt = s_zst.signals["thr_a_norm"]
    assert len(vt) == 4
    np.testing.assert_allclose([vt[0], vt[-1]], [0.0, 0.8])


def test_zstd_corrupt_errors_clearly(tmp_path):
    import shutil

    if shutil.which("zstd") is None:
        pytest.skip("zstd CLI not on PATH")
    bad = tmp_path / "broken.jsonl.zst"
    bad.write_bytes(b"this is not a zstd frame at all")
    with pytest.raises(RuntimeError, match="zstd failed to decompress"):
        Session(bad)
