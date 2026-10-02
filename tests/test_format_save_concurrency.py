"""Concurrent atomic-save regressions using only synthetic .li* files."""

import json
import multiprocessing
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from formats import base
from formats.base import LitFormat


class _RaceFormat(LitFormat):
    SCHEMA_FILE = "__missing_test_schema__.json"

    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}

    @classmethod
    def from_dict(cls, data):
        return cls(data["value"])


def _save_in_process(path, value, started, other_finished, results, pause_after_partial):
    import formats.base as base_module

    original_replace = Path.replace

    def record_replace(self, target):
        results.put(("temp", value, self.name))
        return original_replace(self, target)

    Path.replace = record_replace
    if pause_after_partial:
        def held_dump(obj, stream, **kwargs):
            stream.write('{"value":')
            stream.flush()
            started.set()
            if not other_finished.wait(15):
                raise TimeoutError("zweiter Schreibprozess wurde nicht fertig")
            stream.write(json.dumps(obj["value"]))
            stream.write("}")

        base_module.json.dump = held_dump
    else:
        if not started.wait(15):
            results.put(("error", value, "erster Schreibprozess startete nicht"))
            return

    try:
        _RaceFormat(value).save(Path(path))
        results.put(("ok", value, None))
    except OSError as exc:  # return filesystem failures to the parent assertion
        results.put(("error", value, f"{type(exc).__name__}: {exc}"))
    finally:
        if not pause_after_partial:
            other_finished.set()


def test_two_process_saves_use_distinct_temps_and_publish_valid_json(tmp_path):
    context = multiprocessing.get_context("spawn")
    started = context.Event()
    second_finished = context.Event()
    results = context.Queue()
    target = tmp_path / "shared.litask"

    first = context.Process(
        target=_save_in_process,
        args=(str(target), "A", started, second_finished, results, True),
    )
    second = context.Process(
        target=_save_in_process,
        args=(str(target), "B", started, second_finished, results, False),
    )
    first.start()
    second.start()
    first.join(20)
    second.join(20)

    if first.is_alive():
        first.terminate()
        first.join()
    if second.is_alive():
        second.terminate()
        second.join()

    assert first.exitcode == 0
    assert second.exitcode == 0
    received = [results.get(timeout=2) for _ in range(4)]
    assert sorted(item[0] for item in received).count("ok") == 2, received
    temp_names = [item[2] for item in received if item[0] == "temp"]
    assert len(temp_names) == 2
    assert len(set(temp_names)) == 2
    assert json.loads(target.read_text(encoding="utf-8")) == {"value": "A"}
    assert list(tmp_path.iterdir()) == [target]


def test_serialization_failure_preserves_destination_and_removes_own_temp(tmp_path, monkeypatch):
    target = tmp_path / "existing.litask"
    original = '{"value": "München"}\n'.encode()
    target.write_bytes(original)
    foreign_temp = tmp_path / "existing.litask.tmp"
    foreign_temp.write_bytes(b"foreign temporary data")

    def partial_failure(obj, stream, **kwargs):
        stream.write('{"value":')
        stream.flush()
        raise OSError("synthetic serialization failure")

    monkeypatch.setattr(base.json, "dump", partial_failure)
    try:
        _RaceFormat("new").save(target)
    except OSError as exc:
        assert str(exc) == "synthetic serialization failure"
    else:
        raise AssertionError("Save hätte den Serialisierungsfehler weitergeben müssen")

    assert target.read_bytes() == original
    assert foreign_temp.read_bytes() == b"foreign temporary data"
    assert set(tmp_path.iterdir()) == {target, foreign_temp}


def test_save_keeps_utf8_json_contract_and_leaves_legacy_temp_untouched(tmp_path):
    target = tmp_path / "unicode.litask"
    legacy_temp = tmp_path / "unicode.litask.tmp"
    legacy_temp.write_bytes(b"do not modify")

    _RaceFormat("Größe – München").save(target)

    encoded = target.read_bytes()
    expected = json.dumps(
        {"value": "Größe – München"}, ensure_ascii=False, indent=2, default=str
    ).replace("\n", os.linesep).encode("utf-8")
    assert encoded == expected
    assert "Größe – München".encode() in encoded
    assert b"\\u00f6" not in encoded
    assert json.loads(encoded.decode("utf-8")) == {"value": "Größe – München"}
    assert legacy_temp.read_bytes() == b"do not modify"
    assert set(tmp_path.iterdir()) == {target, legacy_temp}
