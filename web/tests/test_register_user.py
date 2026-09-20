import pytest


def test_register_success(client):
    response = client.post("/auth/register", json={
        "login": "test_user",
        "password": "Password123"
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["login"] == "test_user"
    assert "id" in data["user"]


def test_register_missing_password(client):
    response = client.post("/auth/register", json={
        "login": "test_user"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_register_missing_login(client):
    response = client.post("/auth/register", json={
        "password": "Password123"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize("invalid_login", [
    "abc",  # Слишком короткий (< 4)
    "this_login_is_way_too_long_123",  # Слишком длинный (> 20)
    "user@name",  # Недопустимый символ "@"
    "user name"  # Пробел
])
def test_register_invalid_login(client, invalid_login):
    response = client.post("/auth/register", json={
        "login": invalid_login,
        "password": "Password123"
    })
    assert response.status_code == 400
    assert "Login must be" in response.get_json()["error"]


@pytest.mark.parametrize("invalid_password", [
    "short1",  # Слишком короткий (< 6)
    "alllowercase1",  # Нет заглавной буквы
    "ALLUPPERCASE1",  # Нет строчной буквы
    "NoDigitsHere",  # Нет цифры
    "toolongpassword12345678901234567890"  # Слишком длинный (> 32)
])
def test_register_invalid_password(client, invalid_password):
    response = client.post("/auth/register", json={
        "login": "test_user",
        "password": invalid_password
    })
    assert response.status_code == 400
    assert "Password must be" in response.get_json()["error"]


def test_register_duplicate_user(client):
    payload = {
        "login": "test_user",
        "password": "Password123"
    }
    
    response_first = client.post("/auth/register", json=payload)
    assert response_first.status_code == 201
    
    response_second = client.post("/auth/register", json=payload)
    assert response_second.status_code == 400
    assert response_second.get_json()["error"] == "User with this login already exists"
