from markupsafe import escape


def test_get_posts_success(client, auth_headers):
    headers = auth_headers(login="user_posts", password="Password123")
    
    client.post('/api/data', json={
        "title": "First Post",
        "description": "First description"
    }, headers=headers)
    
    client.post('/api/data', json={
        "title": "Second Post",
        "description": "Second description"
    }, headers=headers)
    
    response = client.get('/api/data', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "First Post"
    assert data[1]["title"] == "Second Post"


def test_get_posts_unauthorized(client):
    response = client.get('/api/data')
    
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_get_posts_xss_protection(client, auth_headers):
    headers = auth_headers(login="user_xss", password="Password123")
    
    xss_payload = "<script>alert('XSS')</script>"
    expected_escaped = str(escape(xss_payload))
    
    client.post('/api/data', json={
        "title": xss_payload,
        "description": xss_payload
    }, headers=headers)
    
    response = client.get('/api/data', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data[0]["title"] == expected_escaped
    assert data[0]["description"] == expected_escaped


def test_create_post_sql_injection(client, auth_headers):
    headers = auth_headers(login="sql_user", password="Password123")
    
    sql_payload = "'; DROP TABLE posts; --"
    expected_escaped = str(escape(sql_payload))
    
    response = client.post('/api/data', json={
        "title": sql_payload,
        "description": "Normal description"
    }, headers=headers)
    
    assert response.status_code == 201
    
    get_response = client.get('/api/data', headers=headers)
    assert get_response.status_code == 200
    data = get_response.get_json()
    
    assert len(data) == 1
    assert data[0]["title"] == expected_escaped
