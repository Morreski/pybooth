import os

from pybooth.event_log import EventLog, EventReader


def test_reader():
    path = "/tmp/test_event.log"
    open(path, "w")
    try:
        log = EventLog(path)
        reader = EventReader(path)
        log.notify("HELLO", {"message": "This is a test"})
        assert next(reader) == {"event": "HELLO", "data": {"message": "This is a test"}}
    finally:
        os.remove(path)


def test_reader_skip_past():
    path = "/tmp/test_event.log"
    open(path, "w")
    try:
        log = EventLog(path)
        log.notify("HELLO", {"message": "This is a test"})
        reader = EventReader(path)
        log.notify("HELLO", {"message": "This is a second test"})
        events = list(reader)
        assert len(events) == 1
        assert events[0] == {
            "event": "HELLO",
            "data": {"message": "This is a second test"},
        }
    finally:
        os.remove(path)


def test_reader_no_skip_past():
    path = "/tmp/test_event.log"
    open(path, "w")
    try:
        log = EventLog(path)
        log.notify("HELLO", {"message": "This is a test"})
        reader = EventReader(path, skip_past=False)
        log.notify("HELLO", {"message": "This is a second test"})
        events = list(reader)
        assert len(events) == 2
        assert events[0] == {
            "event": "HELLO",
            "data": {"message": "This is a test"},
        }
        assert events[1] == {
            "event": "HELLO",
            "data": {"message": "This is a second test"},
        }
    finally:
        os.remove(path)
