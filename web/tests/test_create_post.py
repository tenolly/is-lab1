def test_create_post_success(client, auth_headers):
    headers = auth_headers(login="author_user", password="Password123")
    
    response = client.post('/api/data', json={
        "title": "Test Post Title",
        "description": "Test post description content."
    }, headers=headers)
    
    assert response.status_code == 201, response.get_json()
    
    data = response.get_json()
    assert data["message"] == "Post created successfully"
    assert data["post"]["title"] == "Test Post Title"
    assert data["post"]["description"] == "Test post description content."
    assert "id" in data["post"]


def test_create_post_unauthorized(client):
    response = client.post('/api/data', json={
        "title": "Unauthorized Post",
        "description": "Should fail."
    })
    
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_create_post_missing_title(client, auth_headers):
    headers = auth_headers(login="author_user2", password="Password123")
    
    response = client.post('/api/data', json={
        "description": "Only description provided."
    }, headers=headers)
    
    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"
