def test_auth_flow(client):
    email = "user1@example.com"
    password = "secret123"
    # signup
    r = client.post('/api/v1/auth/signup', json={'email': email, 'password': password})
    assert r.status_code in (200, 400)
    # login
    r = client.post('/api/v1/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    # me
    r = client.get('/api/v1/auth/me')
    assert r.status_code == 200
    assert r.json().get('email') == email
    # logout
    r = client.post('/api/v1/auth/logout')
    assert r.status_code == 200
