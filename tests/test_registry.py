import pytest

from dataflow import SOURCES, STEPS, RegistryError, Registry, Step, Source


def test_default_components_are_registered():
    assert {"csv", "json", "memory"} <= set(SOURCES.names())
    assert {"filter", "map", "rename", "select", "drop", "cast", "deduplicate", "sort"} <= set(STEPS.names())


def test_register_and_create_custom_component():
    registry = Registry("step", Step)

    @registry.register("Noop")
    class Noop(Step):
        def process(self, records):
            return records

    assert "noop" in registry
    assert isinstance(registry.create("NOOP"), Noop)


def test_duplicate_name_is_rejected_unless_overwrite():
    registry = Registry("step", Step)

    class A(Step):
        def process(self, records):
            return records

    registry.add("a", A)
    with pytest.raises(RegistryError):
        registry.add("a", A)
    registry.add("a", A, overwrite=True)


def test_registering_wrong_type_is_rejected():
    registry = Registry("step", Step)
    with pytest.raises(RegistryError):
        registry.add("x", Source)  # type: ignore[arg-type]


def test_unknown_name_lists_available_components():
    with pytest.raises(RegistryError, match="Disponíveis"):
        STEPS.create("inexistente")
