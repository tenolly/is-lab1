import pytest
from models import db
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def register_user(client):
    def _register(login="login_user", password="Password123"):
        response = client.post('/auth/register', json={
            "login": login,
            "password": password
        })
        assert response.status_code == 201, f"Failed to register user: {response.get_json()}"
        return response
    return _register


@pytest.fixture
def auth_headers(client, register_user):
    def _get_headers(login="login_user", password="Password123"):
        register_user(login=login, password=password)
        
        response = client.post('/auth/login', json={
            "login": login,
            "password": password
        })
        assert response.status_code == 200, f"Failed to login user: {response.get_json()}"
        
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _get_headers
