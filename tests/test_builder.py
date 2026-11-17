import pytest

from dataflow import (
    ConfigurationError, FilterStep, MemorySink, PipelineBuilder, PipelineObserver, RegistryError,
)


def test_fluent_build_by_name_and_by_instance(people):
    sink = MemorySink()
    pipeline = (
        PipelineBuilder("x")
        .source("memory", records=people)
        .step("deduplicate")
        .step(FilterStep(lambda r: r["name"] == "Bruno"))
        .sink(sink)
        .build()
    )
    pipeline.run()
    assert len(sink.records) == 1 and pipeline.name == "x"


def test_options_with_instance_are_rejected():
    with pytest.raises(ConfigurationError):
        PipelineBuilder().step(FilterStep(lambda r: True), predicate=None)


def test_invalid_component_is_rejected():
    with pytest.raises(ConfigurationError):
        PipelineBuilder().step(123)  # type: ignore[arg-type]
    with pytest.raises(ConfigurationError):
        PipelineBuilder().observe(object())  # type: ignore[arg-type]


def test_unknown_name_raises_registry_error():
    with pytest.raises(RegistryError):
        PipelineBuilder().step("nao_existe")


def test_from_config(tmp_path, people):
    out = tmp_path / "out.json"
    config = {
        "name": "cfg",
        "source": {"type": "memory", "records": people},
        "steps": [
            {"type": "deduplicate"},
            {"type": "cast", "types": {"age": int}},
            {"type": "rename", "mapping": {"name": "nome"}},
        ],
        "sink": {"type": "json", "path": out},
    }
    result = PipelineBuilder.from_config(config).build().run()
    assert result[0] == {"id": "1", "nome": "Ana", "age": 34}
    assert out.exists()


def test_from_config_requires_type():
    with pytest.raises(ConfigurationError):
        PipelineBuilder.from_config({"steps": [{"mapping": {}}]})


def test_builder_is_independent_of_observer_subclass(people):
    class Counter(PipelineObserver):
        calls = 0

        def on_pipeline_end(self, pipeline_name, output_count, elapsed):
            Counter.calls += 1

    PipelineBuilder().source("memory", records=people).observe(Counter()).build().run()
    assert Counter.calls == 1
