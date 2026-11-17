import json

import pytest

from dataflow import ConfigurationError, CsvSink, CsvSource, JsonSink, JsonSource, MemorySink, MemorySource


def test_csv_roundtrip(tmp_path, people):
    path = tmp_path / "p.csv"
    CsvSink(path).write(people)
    assert CsvSource(path).read() == people


def test_csv_custom_delimiter(tmp_path):
    path = tmp_path / "p.csv"
    path.write_text("a;b\n1;2\n", encoding="utf-8")
    assert CsvSource(path, delimiter=";").read() == [{"a": "1", "b": "2"}]


def test_json_roundtrip_keeps_unicode(tmp_path):
    path = tmp_path / "p.json"
    JsonSink(path).write([{"nome": "José"}])
    assert "José" in path.read_text(encoding="utf-8")
    assert JsonSource(path).read() == [{"nome": "José"}]


def test_json_source_rejects_non_list(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(json.dumps({"a": 1}), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        JsonSource(path).read()


def test_memory_source_and_sink_copy_data(people):
    sink = MemorySink()
    sink.write(MemorySource(people).read())
    sink.records[0]["name"] = "X"
    assert people[0]["name"] == "Ana"
