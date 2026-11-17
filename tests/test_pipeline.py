import pytest

from dataflow import (
    ConfigurationError, FilterStep, MemorySink, MemorySource, MetricsObserver, Pipeline,
    PipelineObserver, StageExecutionError, Step,
)


class Recorder(PipelineObserver):
    def __init__(self):
        self.events = []

    def on_pipeline_start(self, pipeline_name):
        self.events.append(("start", pipeline_name))

    def on_step_start(self, step_name, input_count):
        self.events.append(("step_start", step_name, input_count))

    def on_step_end(self, step_name, input_count, output_count, elapsed):
        self.events.append(("step_end", step_name, input_count, output_count))

    def on_error(self, stage, error):
        self.events.append(("error", stage))

    def on_pipeline_end(self, pipeline_name, output_count, elapsed):
        self.events.append(("end", output_count))


class Boom(Step):
    def process(self, records):
        raise ValueError("falhou")


def test_runs_with_inline_records(people):
    pipeline = Pipeline(steps=[FilterStep(lambda r: r["name"] == "Ana")])
    assert len(pipeline.run(people)) == 1


def test_runs_source_steps_sink(people):
    sink = MemorySink()
    Pipeline(source=MemorySource(people), steps=[FilterStep(lambda r: r["age"] == "34")], sink=sink).run()
    assert [r["name"] for r in sink.records] == ["Ana"]


def test_requires_exactly_one_data_origin(people):
    with pytest.raises(ConfigurationError):
        Pipeline().run()
    with pytest.raises(ConfigurationError):
        Pipeline(source=MemorySource(people)).run(people)


def test_observer_receives_events_in_order(people):
    rec = Recorder()
    Pipeline(steps=[FilterStep(lambda r: r["name"] == "Ana")], observers=[rec], name="p").run(people)
    assert rec.events == [
        ("start", "p"),
        ("step_start", "FilterStep", 3),
        ("step_end", "FilterStep", 3, 1),
        ("end", 1),
    ]


def test_error_is_wrapped_and_observers_are_notified(people):
    rec, metrics = Recorder(), MetricsObserver()
    pipeline = Pipeline(steps=[Boom()], observers=[rec, metrics])
    with pytest.raises(StageExecutionError) as info:
        pipeline.run(people)
    assert info.value.stage == "Boom"
    assert isinstance(info.value.original, ValueError)
    assert ("error", "Boom") in rec.events
    assert metrics.errors[0][0] == "Boom"
    assert not any(e[0] == "end" for e in rec.events)


def test_metrics_observer_collects_step_metrics(people):
    metrics = MetricsObserver()
    Pipeline(steps=[FilterStep(lambda r: True)], observers=[metrics]).run(people)
    assert metrics.steps[0].input_count == 3
    assert metrics.steps[0].output_count == 3
    assert metrics.total_elapsed >= 0


def test_input_records_are_not_mutated(people):
    Pipeline(steps=[FilterStep(lambda r: False)]).run(people)
    assert len(people) == 3
