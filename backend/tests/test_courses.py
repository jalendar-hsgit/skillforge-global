def test_list_courses(client):
    r = client.get('/api/v1/courses')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
