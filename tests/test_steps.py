from dataflow import (
    CastStep, DeduplicateStep, DropStep, FilterStep, MapStep, RenameStep, SelectStep, SortStep,
)


def test_filter(people):
    assert [r["name"] for r in FilterStep(lambda r: r["name"] == "Ana").process(people)] == ["Ana"]


def test_map_does_not_mutate_input(people):
    out = MapStep(lambda r: {**r, "name": r["name"].upper()}).process(people)
    assert out[0]["name"] == "ANA"
    assert people[0]["name"] == "Ana"


def test_rename(people):
    assert RenameStep({"name": "nome"}).process(people)[0] == {"id": "1", "nome": "Ana", "age": "34"}


def test_select_and_drop(people):
    assert SelectStep(["name"]).process(people)[0] == {"name": "Ana"}
    assert DropStep(["age"]).process(people)[0] == {"id": "1", "name": "Ana"}


def test_cast(people):
    assert CastStep({"age": int}).process(people)[0]["age"] == 34


def test_deduplicate_whole_record_and_by_key(people):
    assert len(DeduplicateStep().process(people)) == 2
    assert len(DeduplicateStep(["age"]).process(people)) == 2


def test_sort(people):
    assert [r["name"] for r in SortStep("name", reverse=True).process(people)][0] == "Bruno"
    assert SortStep(lambda r: int(r["age"])).process(people)[0]["name"] == "Bruno"
