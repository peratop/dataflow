"""Builder: construção fluente e validada de pipelines."""
from __future__ import annotations

from typing import Any

from .core import Sink, Source, Step
from .errors import ConfigurationError
from .observers import PipelineObserver
from .pipeline import Pipeline
from .registry import SINKS, SOURCES, STEPS, Registry


class PipelineBuilder:
    """Monta um :class:`Pipeline` passo a passo.

    Cada método aceita uma instância pronta OU o nome registrado + opções::

        PipelineBuilder().source("csv", path="in.csv").step("rename", mapping={...}).build()
    """

    def __init__(self, name: str = "pipeline") -> None:
        self._name = name
        self._source: Source | None = None
        self._steps: list[Step] = []
        self._sink: Sink | None = None
        self._observers: list[PipelineObserver] = []

    def source(self, source: Source | str, **options: Any) -> "PipelineBuilder":
        self._source = self._resolve(source, SOURCES, Source, options)
        return self

    def step(self, step: Step | str, **options: Any) -> "PipelineBuilder":
        self._steps.append(self._resolve(step, STEPS, Step, options))
        return self

    def sink(self, sink: Sink | str, **options: Any) -> "PipelineBuilder":
        self._sink = self._resolve(sink, SINKS, Sink, options)
        return self

    def observe(self, observer: PipelineObserver) -> "PipelineBuilder":
        if not isinstance(observer, PipelineObserver):
            raise ConfigurationError("O observer deve herdar de PipelineObserver.")
        self._observers.append(observer)
        return self

    def build(self) -> Pipeline:
        return Pipeline(
            source=self._source,
            steps=self._steps,
            sink=self._sink,
            observers=self._observers,
            name=self._name,
        )

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "PipelineBuilder":
        """Cria o builder a partir de um dicionário (ex.: carregado de JSON).

        Formato::

            {"name": "x",
             "source": {"type": "csv", "path": "in.csv"},
             "steps": [{"type": "rename", "mapping": {"a": "b"}}],
             "sink": {"type": "json", "path": "out.json"}}
        """
        builder = cls(config.get("name", "pipeline"))
        if "source" in config:
            kind, options = cls._split_type(config["source"])
            builder.source(kind, **options)
        for step_config in config.get("steps", []):
            kind, options = cls._split_type(step_config)
            builder.step(kind, **options)
        if "sink" in config:
            kind, options = cls._split_type(config["sink"])
            builder.sink(kind, **options)
        return builder

    @staticmethod
    def _split_type(component_config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if "type" not in component_config:
            raise ConfigurationError(f"Configuração sem o campo \"type\": {component_config}")
        options = dict(component_config)
        return options.pop("type"), options

    @staticmethod
    def _resolve(component: Any, registry: Registry, base: type, options: dict[str, Any]) -> Any:
        if isinstance(component, str):
            return registry.create(component, **options)
        if isinstance(component, base):
            if options:
                raise ConfigurationError(
                    "Opções só podem ser usadas junto com o nome de um componente registrado."
                )
            return component
        raise ConfigurationError(f"Esperado {base.__name__} ou nome registrado, recebido: {component!r}")
