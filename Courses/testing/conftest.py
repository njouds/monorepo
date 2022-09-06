import pytest
from conftest import ScopedSession, base_db  # type: ignore
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True, scope="session")
def seed_data(client: TestClient):

    db_connection = base_db.engine.connect()
    db_connection.begin()
    _ = ScopedSession(bind=db_connection)
    print('<=======> scope="session" <=======>')

    """
    run direct queries or better, hit the endpoints that generate the data you want
    """

    print('<=======> scope="session" <=======>')
    ScopedSession.remove()
    db_connection.commit()
