from typing import Generator

import pytest
from pydantic import BaseModel
from app import schema as s


class TestData(BaseModel):
    __test__ = False

    test_user: s.UserCreate | None
    test_users: list[s.UserCreate]

    # authorized
    test_authorized_users: list[s.UserCreate]
    test_superuser: s.UserCreate | None


@pytest.fixture
def test_data() -> Generator[TestData, None, None]:
    yield TestData.parse_file("tests/test_data.json")
