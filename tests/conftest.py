import pytest


@pytest.fixture
def people():
    return [
        {"id": "1", "name": "Ana", "age": "34"},
        {"id": "2", "name": "Bruno", "age": "17"},
        {"id": "2", "name": "Bruno", "age": "17"},
    ]
