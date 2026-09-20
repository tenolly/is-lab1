def test_login_success(client, register_user):
    register_user(login="my_login", password="Password123")
    
    response = client.post("/auth/login", json={
        "login": "my_login",
        "password": "Password123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


def test_login_missing_login(client):
    response = client.post("/auth/login", json={
        "password": "Password123"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_login_missing_password(client):
    response = client.post("/auth/login", json={
        "login": "login_user"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_login_wrong_login(client, register_user):
    register_user(login="login_user", password="Password123")
    
    response = client.post("/auth/login", json={
        "login": "unknown_user",
        "password": "Password123"
    })
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"


def test_login_wrong_password(client, register_user):
    register_user(login="login_user", password="Password123")

    response = client.post("/auth/login", json={
        "login": "login_user",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"
