from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={"email": "missing@example.org"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    data = {"email": "new@example.org", "name": "New User"}
    try:
        response = client.post("/api/v1/user", json=data)
        assert response.status_code == 201
        saved = client.get("/api/v1/user", params={"email": data["email"]})
        assert saved.json() == {"id": response.json(), **data}
    finally:
        client.delete("/api/v1/user", params={"email": data["email"]})

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    data = {"email": users[0]["email"], "name": "Duplicate"}
    response = client.post("/api/v1/user", json=data)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"

def test_delete_user():
    '''Удаление пользователя'''
    params = {"email": "remove@example.org"}
    created = client.post("/api/v1/user", json={**params, "name": "Remove Me"})
    assert created.status_code == 201
    response = client.delete("/api/v1/user", params=params)
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/v1/user", params=params).status_code == 404
