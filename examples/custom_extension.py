"""Extensão pelo cliente: nova Source (XML), novo Step e novo Observer.

Nada dentro de src/dataflow é alterado (Open/Closed Principle).
"""
import xml.etree.ElementTree as ET
from pathlib import Path

from dataflow import (
    SOURCES, STEPS, MemorySink, PipelineBuilder, PipelineObserver, Records, Source, Step,
)

DATA = Path(__file__).parent / "data" / "clientes.xml"


@SOURCES.register("xml")
class XmlSource(Source):
    """Lê <raiz><item><campo>valor</campo></item></raiz> como lista de dicts."""

    def __init__(self, path):
        self._path = path

    def read(self) -> Records:
        root = ET.parse(self._path).getroot()
        return [{child.tag: child.text for child in item} for item in root]


@STEPS.register("normalize_email")
class NormalizeEmailStep(Step):
    def process(self, records: Records) -> Records:
        return [{**r, "email": r["email"].strip().lower()} for r in records]


class PrintObserver(PipelineObserver):
    def on_step_end(self, step_name, input_count, output_count, elapsed):
        print(f"[observer] {step_name}: {input_count} -> {output_count}")


sink = MemorySink()
(
    PipelineBuilder("clientes-xml")
    .source("xml", path=DATA)                      # source criada pelo cliente
    .step("normalize_email")                       # step criado pelo cliente
    .step("cast", types={"idade": int})            # step da biblioteca
    .step("filter", predicate=lambda r: r["idade"] >= 18)
    .sink(sink)
    .observe(PrintObserver())                      # observer criado pelo cliente
    .build()
    .run()
)

print("\nResultado:")
for registro in sink.records:
    print(" ", registro)
