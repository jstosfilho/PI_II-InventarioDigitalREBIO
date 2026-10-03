from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def fake_db():
    db = MagicMock()
    db.execute.return_value.scalar.return_value = "3.4 USE_GEOS=1"
    return db


@pytest.fixture
def client(fake_db):
    app.dependency_overrides[get_db] = lambda: fake_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
