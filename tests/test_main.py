import pytest

from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base
from app.dependencies import get_db
from app.core.config import settings



def test_app_is_running(client):
    response = client.get("/")

    assert response.status_code == 200


def test_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


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
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_register_user(client, db):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    user = db.query(User).filter(
        User.username == "testuser"
    ).first()

    assert user is not None
    assert user.username == "testuser"
    assert user.password_hash != "password123"


def test_duplicate_registration(client):
    data = {
        "username": "duplicateuser",
        "password": "password123"
    }

    first_response = client.post(
        "/auth/register",
        json=data
    )

    second_response = client.post(
        "/auth/register",
        json=data
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username already exists"

def test_login(client):
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_authenticated_me(client):
    client.post(
        "/auth/register",
        json={
            "username": "authuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "authuser",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["username"] == "authuser"

def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "wrongpassuser",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_refresh_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "refreshuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "refreshuser",
            "password": "password123"
        }
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_access_token_cannot_refresh(client):
    client.post(
        "/auth/register",
        json={
            "username": "tokenuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "tokenuser",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token required"

def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks/",
        json={"title": "Learn Pytest"},
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Learn Pytest"
    assert data["completed"] is False
    assert "id" in data

def test_get_tasks(client):
    client.post(
        "/auth/register",
        json={
            "username": "getuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "getuser",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    client.post(
        "/tasks/",
        json={"title": "Task One"},
        headers=headers
    )

    client.post(
        "/tasks/",
        json={"title": "Task Two"},
        headers=headers
    )

    response = client.get(
        "/tasks/",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task One"
    assert tasks[1]["title"] == "Task Two"

def test_user_cannot_access_another_users_task(client):
    # User 1
    client.post(
        "/auth/register",
        json={
            "username": "userone",
            "password": "password123"
        }
    )

    login1 = client.post(
        "/auth/login",
        data={
            "username": "userone",
            "password": "password123"
        }
    )

    token1 = login1.json()["access_token"]

    task_response = client.post(
        "/tasks/",
        json={"title": "Private Task"},
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    task_id = task_response.json()["id"]

    # User 2
    client.post(
        "/auth/register",
        json={
            "username": "usertwo",
            "password": "password123"
        }
    )

    login2 = client.post(
        "/auth/login",
        data={
            "username": "usertwo",
            "password": "password123"
        }
    )

    token2 = login2.json()["access_token"]

    # User 2 tries to delete User 1's task
    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404

def test_update_task(client):
    client.post(
        "/auth/register",
        json={
            "username": "updateuser",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "updateuser",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/tasks/",
        json={"title": "Old Title"},
        headers=headers
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "New Title",
            "completed": True
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Title"
    assert data["completed"] is True

def test_delete_task(client):
    client.post(
        "/auth/register",
        json={"username": "deleteuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "deleteuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/tasks/",
        json={"title": "Task to Delete"},
        headers=headers
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

def test_user_cannot_update_another_users_task(client):
    # User 1
    client.post(
        "/auth/register",
        json={"username": "updateuser1", "password": "password123"}
    )

    login1 = client.post(
        "/auth/login",
        data={"username": "updateuser1", "password": "password123"}
    )

    token1 = login1.json()["access_token"]

    task_response = client.post(
        "/tasks/",
        json={"title": "Private Task"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    task_id = task_response.json()["id"]

    # User 2
    client.post(
        "/auth/register",
        json={"username": "updateuser2", "password": "password123"}
    )

    login2 = client.post(
        "/auth/login",
        data={"username": "updateuser2", "password": "password123"}
    )

    token2 = login2.json()["access_token"]

    # User 2 tries to update User 1's task
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Hacked Task"},
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 404

def test_user_cannot_delete_another_users_task(client):
    # User 1
    client.post(
        "/auth/register",
        json={"username": "deleteuser1", "password": "password123"}
    )

    login1 = client.post(
        "/auth/login",
        data={"username": "deleteuser1", "password": "password123"}
    )

    token1 = login1.json()["access_token"]

    task_response = client.post(
        "/tasks/",
        json={"title": "Protected Task"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    task_id = task_response.json()["id"]

    # User 2
    client.post(
        "/auth/register",
        json={"username": "deleteuser2", "password": "password123"}
    )

    login2 = client.post(
        "/auth/login",
        data={"username": "deleteuser2", "password": "password123"}
    )

    token2 = login2.json()["access_token"]

    # User 2 tries to delete User 1's task
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 404

    # Verify the task still exists for User 1
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Protected Task"

def test_task_pagination(client):
    client.post(
        "/auth/register",
        json={"username": "pageuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "pageuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create 5 tasks
    for i in range(1, 6):
        client.post(
            "/tasks/",
            json={"title": f"Task {i}"},
            headers=headers
        )

    # Get only 2 tasks
    response = client.get(
        "/tasks/?skip=0&limit=2",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"

    # Skip first 2 tasks
    response = client.get(
        "/tasks/?skip=2&limit=2",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 3"
    assert tasks[1]["title"] == "Task 4"

def test_completed_filter(client):
    client.post(
        "/auth/register",
        json={"username": "filteruser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "filteruser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 tasks
    client.post(
        "/tasks/",
        json={"title": "Pending Task"},
        headers=headers
    )

    client.post(
        "/tasks/",
        json={"title": "Completed Task"},
        headers=headers
    )

    client.post(
        "/tasks/",
        json={"title": "Another Pending Task"},
        headers=headers
    )

    # Mark second task as completed
    client.put(
        "/tasks/2",
        json={"completed": True},
        headers=headers
    )

    # Get completed tasks
    response = client.get(
        "/tasks/?completed=true",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Completed Task"
    assert tasks[0]["completed"] is True

    # Get incomplete tasks
    response = client.get(
        "/tasks/?completed=false",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert all(task["completed"] is False for task in tasks)

def test_task_search(client):
    client.post(
        "/auth/register",
        json={"username": "searchuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "searchuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create tasks
    client.post(
        "/tasks/",
        json={"title": "Learn Python"},
        headers=headers
    )

    client.post(
        "/tasks/",
        json={"title": "Learn FastAPI"},
        headers=headers
    )

    client.post(
        "/tasks/",
        json={"title": "Python Database Project"},
        headers=headers
    )

    # Search for "python"
    response = client.get(
        "/tasks/?search=python",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2
    assert tasks[0]["title"] == "Learn Python"
    assert tasks[1]["title"] == "Python Database Project"

def test_task_sorting(client):
    client.post(
        "/auth/register",
        json={"username": "sortuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "sortuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create tasks in unsorted order
    for title in ["Zebra", "Apple", "Mango"]:
        client.post(
            "/tasks/",
            json={"title": title},
            headers=headers
        )

    # Ascending
    response = client.get(
        "/tasks/?sort_by=title&order=asc",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert [task["title"] for task in tasks] == [
        "Apple",
        "Mango",
        "Zebra"
    ]

    # Descending
    response = client.get(
        "/tasks/?sort_by=title&order=desc",
        headers=headers
    )

    assert response.status_code == 200

    tasks = response.json()

    assert [task["title"] for task in tasks] == [
        "Zebra",
        "Mango",
        "Apple"
    ]

def test_invalid_sort_field(client):
    client.post(
        "/auth/register",
        json={"username": "invalidsortuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "invalidsortuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/tasks/?sort_by=password",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sort field"

def test_invalid_sort_order(client):
    client.post(
        "/auth/register",
        json={"username": "invalidorderuser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "invalidorderuser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/tasks/?order=random",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order must be asc or desc"

def test_admin_authorization(client, db):
    # Create normal user
    client.post(
        "/auth/register",
        json={"username": "normaluser", "password": "password123"}
    )

    login_response = client.post(
        "/auth/login",
        data={"username": "normaluser", "password": "password123"}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Normal user should be rejected
    response = client.get(
        "/auth/admin",
        headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

    # Make the same user an admin
    from app.models.user import User

    user = db.query(User).filter(
        User.username == "normaluser"
    ).first()

    user.role = "admin"
    db.commit()

    # Login again to get a JWT containing the updated role if needed
    login_response = client.post(
        "/auth/login",
        data={"username": "normaluser", "password": "password123"}
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"