"""Timeline events: markers, notes, and freeze frames for investigations.

A run config carries a Timeline; events render as markers on the graphs,
notes pop up an annotation card on the panel, and freeze frames hold the
video on a still frame while an explanation is shown.

Event kinds:
  marker  - vertical tick on graphs + timestamp in header (cheap, always on)
  note    - annotation card shown while t in [time, time+duration)
  freeze  - like note, plus the compositor holds the video frame still
            for [time, time+duration) so viewers can inspect the moment
"""


class Event:
    def __init__(self, time, label, kind="marker", duration=0.0, text=""):
        self.time = float(time)
        self.label = label
        self.kind = kind
        self.duration = float(duration)
        self.text = text

    def active(self, t):
        if self.kind == "marker":
            return False
        return self.time <= t < self.time + max(self.duration, 0.001)


class Timeline:
    def __init__(self, events=None):
        self.events = sorted(events or [], key=lambda e: e.time)

    @classmethod
    def from_dicts(cls, dicts):
        return cls([Event(**d) for d in dicts])

    def markers(self):
        return [e for e in self.events if e.kind == "marker"]

    def active_note(self, t):
        """The note/freeze event active at time t, or None."""
        for e in self.events:
            if e.kind in ("note", "freeze") and e.active(t):
                return e
        return None

    def upcoming_marker(self, t, within=5.0):
        for e in self.events:
            if e.kind == "marker" and e.time >= t:
                return e if e.time - t <= within else None
        return None
