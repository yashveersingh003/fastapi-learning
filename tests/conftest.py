import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.database.database import Base
from app.dependencies import get_db
from app.core.config import settings

TEST_DATABASE_URL = (
    settings.database_url.rsplit("/", 1)[0]
    + "/fastapi_test_db"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    username = "fixtureuser"
    password = "password123"

    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }