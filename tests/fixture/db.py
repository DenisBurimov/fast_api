from typing import Generator

import pytest
from pymongo.database import Database
from pytest_mock_resources import create_mongo_fixture

from app import get_settings, get_db
from .test_data import TestData
from tests.utils import fill_db_by_test_data


mongo = create_mongo_fixture()
cfg = get_settings()


@pytest.fixture
def db(mongo, test_data: TestData) -> Generator[Database, None, None]:
    from app.main import app

    db = mongo[cfg.MONGO_DB]
    fill_db_by_test_data(db, test_data)

    def override_get_db() -> Generator[Database, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield db
