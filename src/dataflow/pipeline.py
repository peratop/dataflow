"""Pipeline: orquestra Source -> Steps -> Sink e notifica os observers."""
from __future__ import annotations

from time import perf_counter
from typing import Callable, Iterable, TypeVar

from .core import Records, Sink, Source, Step
from .errors import ConfigurationError, StageExecutionError
from .observers import PipelineObserver

R = TypeVar("R")


class Pipeline:
    def __init__(
        self,
        source: Source | None = None,
        steps: Iterable[Step] | None = None,
        sink: Sink | None = None,
        observers: Iterable[PipelineObserver] | None = None,
        name: str = "pipeline",
    ) -> None:
        self.name = name
        self.source = source
        self.steps: list[Step] = list(steps or [])
        self.sink = sink
        self._observers: list[PipelineObserver] = list(observers or [])

    def add_observer(self, observer: PipelineObserver) -> None:
        self._observers.append(observer)

    def run(self, records: Records | None = None) -> Records:
        """Executa o pipeline e devolve os registros finais.

        Os dados vêm do ``source`` configurado OU do argumento ``records`` (nunca dos dois).
        """
        if self.source is not None and records is not None:
            raise ConfigurationError("Informe 'records' ou configure um source, não ambos.")
        if self.source is None and records is None:
            raise ConfigurationError("Nenhuma fonte de dados: configure um source ou passe 'records'.")

        started = perf_counter()
        self._notify("on_pipeline_start", self.name)

        if self.source is not None:
            source = self.source
            data = self._guard(f"source:{type(source).__name__}", source.read)
        else:
            data = [dict(r) for r in records or []]

        for step in self.steps:
            data = self._run_step(step, data)

        if self.sink is not None:
            sink = self.sink
            final = data
            self._guard(f"sink:{type(sink).__name__}", lambda: sink.write(final))

        self._notify("on_pipeline_end", self.name, len(data), perf_counter() - started)
        return data

    def _run_step(self, step: Step, data: Records) -> Records:
        count_in = len(data)
        self._notify("on_step_start", step.name, count_in)
        started = perf_counter()
        result = self._guard(step.name, lambda: list(step.process(data)))
        self._notify("on_step_end", step.name, count_in, len(result), perf_counter() - started)
        return result

    def _guard(self, stage: str, action: Callable[[], R]) -> R:
        try:
            return action()
        except Exception as exc:
            self._notify("on_error", stage, exc)
            raise StageExecutionError(stage, exc) from exc

    def _notify(self, event: str, *args) -> None:
        for observer in self._observers:
            getattr(observer, event)(*args)
