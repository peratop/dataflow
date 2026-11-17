"""Observer: permite acompanhar a execução de um pipeline sem acoplá-lo a logging/métricas."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field


class PipelineObserver:
    """Classe base com métodos vazios: o cliente sobrescreve apenas os eventos que lhe interessam."""

    def on_pipeline_start(self, pipeline_name: str) -> None: ...

    def on_step_start(self, step_name: str, input_count: int) -> None: ...

    def on_step_end(self, step_name: str, input_count: int, output_count: int, elapsed: float) -> None: ...

    def on_error(self, stage: str, error: Exception) -> None: ...

    def on_pipeline_end(self, pipeline_name: str, output_count: int, elapsed: float) -> None: ...


class LoggingObserver(PipelineObserver):
    """Envia os eventos do pipeline para o módulo ``logging``."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._log = logger or logging.getLogger("dataflow")

    def on_pipeline_start(self, pipeline_name: str) -> None:
        self._log.info("Pipeline '%s' iniciado", pipeline_name)

    def on_step_end(self, step_name: str, input_count: int, output_count: int, elapsed: float) -> None:
        self._log.info("%s: %d -> %d registros (%.4fs)", step_name, input_count, output_count, elapsed)

    def on_error(self, stage: str, error: Exception) -> None:
        self._log.error("Erro em '%s': %s", stage, error)

    def on_pipeline_end(self, pipeline_name: str, output_count: int, elapsed: float) -> None:
        self._log.info("Pipeline '%s' finalizado: %d registros (%.4fs)", pipeline_name, output_count, elapsed)


@dataclass(frozen=True)
class StepMetric:
    name: str
    input_count: int
    output_count: int
    elapsed: float


@dataclass
class MetricsObserver(PipelineObserver):
    """Coleta métricas por etapa para consulta após a execução."""

    steps: list[StepMetric] = field(default_factory=list)
    errors: list[tuple[str, Exception]] = field(default_factory=list)
    total_elapsed: float = 0.0

    def on_pipeline_start(self, pipeline_name: str) -> None:
        self.steps.clear()
        self.errors.clear()
        self.total_elapsed = 0.0

    def on_step_end(self, step_name: str, input_count: int, output_count: int, elapsed: float) -> None:
        self.steps.append(StepMetric(step_name, input_count, output_count, elapsed))

    def on_error(self, stage: str, error: Exception) -> None:
        self.errors.append((stage, error))

    def on_pipeline_end(self, pipeline_name: str, output_count: int, elapsed: float) -> None:
        self.total_elapsed = elapsed
