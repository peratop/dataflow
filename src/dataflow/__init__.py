"""DataFlow: biblioteca extensível para pipelines de processamento de dados em memória."""
from __future__ import annotations

from .builder import PipelineBuilder
from .core import Record, Records, Sink, Source, Step
from .errors import ConfigurationError, DataFlowError, RegistryError, StageExecutionError
from .observers import LoggingObserver, MetricsObserver, PipelineObserver, StepMetric
from .pipeline import Pipeline
from .registry import SINKS, SOURCES, STEPS, Registry

# Importar os módulos abaixo registra as implementações padrão nos registries.
from .sources import CsvSource, JsonSource, MemorySource
from .steps import (
    CastStep,
    DeduplicateStep,
    DropStep,
    FilterStep,
    MapStep,
    RenameStep,
    SelectStep,
    SortStep,
)
from .sinks import CsvSink, JsonSink, MemorySink

__version__ = "0.1.0"

__all__ = [
    "Pipeline", "PipelineBuilder",
    "Source", "Step", "Sink", "Record", "Records",
    "Registry", "SOURCES", "STEPS", "SINKS",
    "PipelineObserver", "LoggingObserver", "MetricsObserver", "StepMetric",
    "CsvSource", "JsonSource", "MemorySource",
    "FilterStep", "MapStep", "RenameStep", "SelectStep", "DropStep", "CastStep",
    "DeduplicateStep", "SortStep",
    "CsvSink", "JsonSink", "MemorySink",
    "DataFlowError", "ConfigurationError", "RegistryError", "StageExecutionError",
]
