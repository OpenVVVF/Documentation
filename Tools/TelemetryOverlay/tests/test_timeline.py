from telemetry_overlay.timeline import Event, Timeline


def test_event_kinds():
    m = Event(10.0, "m", kind="marker")
    assert not m.active(10.0) and not m.active(12.0)
    n = Event(10.0, "n", kind="note", duration=2.0)
    assert n.active(10.0) and n.active(11.9) and not n.active(12.0)
    f = Event(10.0, "f", kind="freeze", duration=0.0)
    assert f.active(10.0) and not f.active(10.002)  # zero->1ms minimum


def test_timeline_sorting_and_notes():
    tl = Timeline.from_dicts([
        {"time": 30.0, "label": "b", "kind": "note", "duration": 5.0},
        {"time": 10.0, "label": "a", "kind": "marker"},
        {"time": 40.0, "label": "c", "kind": "freeze", "duration": 3.0},
    ])
    assert [e.time for e in tl.events] == [10.0, 30.0, 40.0]
    assert [e.label for e in tl.markers()] == ["a"]
    assert tl.active_note(32.0).label == "b"
    assert tl.active_note(41.0).label == "c"
    assert tl.active_note(20.0) is None


def test_upcoming_marker():
    tl = Timeline.from_dicts([
        {"time": 10.0, "label": "a", "kind": "marker"},
        {"time": 100.0, "label": "b", "kind": "marker"},
    ])
    assert tl.upcoming_marker(9.0, within=5.0).label == "a"
    assert tl.upcoming_marker(4.0, within=5.0) is None  # >5s away
    assert tl.upcoming_marker(50.0, within=5.0) is None
    assert tl.upcoming_marker(10.0, within=5.0).label == "a"  # at marker time
