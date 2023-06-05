from typing import Generator

import pytest
from pymongo.database import Database
from mongomock import MongoClient as MockMongoClient

from app import get_db
from .test_data import TestData
from tests.utils import fill_db_by_test_data


@pytest.fixture
def db(test_data: TestData) -> Generator[Database, None, None]:
    from app.main import app

    db = MockMongoClient().db
    fill_db_by_test_data(db, test_data)

    def override_get_db() -> Generator[Database, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield db
