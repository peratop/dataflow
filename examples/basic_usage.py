"""Caso de uso padrão: apenas componentes que já vêm na biblioteca."""
import logging
import tempfile
from pathlib import Path

from dataflow import LoggingObserver, MetricsObserver, PipelineBuilder

logging.basicConfig(level=logging.INFO, format="%(message)s")

DATA = Path(__file__).parent / "data" / "clientes.csv"
saida = Path(tempfile.mkdtemp()) / "clientes_adultos.json"

metrics = MetricsObserver()

pipeline = (
    PipelineBuilder("clientes-adultos")
    .source("csv", path=DATA)
    .step("deduplicate")
    .step("cast", types={"id": int, "idade": int})
    .step("filter", predicate=lambda r: r["idade"] >= 18)
    .step("rename", mapping={"nome": "name", "cidade": "city"})
    .step("sort", key="name")
    .sink("json", path=saida)
    .observe(LoggingObserver())
    .observe(metrics)
    .build()
)

resultado = pipeline.run()

print("\nResultado:")
for registro in resultado:
    print(" ", registro)
print("\nArquivo gerado em:", saida)
print("Etapas executadas:", [m.name for m in metrics.steps])
