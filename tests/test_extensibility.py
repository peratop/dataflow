"""Prova do Open/Closed: o cliente estende a lib sem tocar em src/dataflow."""
from dataflow import SINKS, SOURCES, STEPS, PipelineBuilder, Records, Sink, Source, Step


def test_client_defined_source_step_and_sink_work_by_name():
    @SOURCES.register("fixed_test")
    class FixedSource(Source):
        def read(self) -> Records:
            return [{"v": 1}, {"v": 2}]

    @STEPS.register("double_test")
    class Double(Step):
        def process(self, records: Records) -> Records:
            return [{"v": r["v"] * 2} for r in records]

    collected: list = []

    @SINKS.register("collect_test")
    class Collect(Sink):
        def write(self, records: Records) -> None:
            collected.extend(records)

    PipelineBuilder().source("fixed_test").step("double_test").sink("collect_test").build().run()
    assert collected == [{"v": 2}, {"v": 4}]
