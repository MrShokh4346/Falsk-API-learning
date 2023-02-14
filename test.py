from app import client


def test_get():
    req = client.get('/api')
    assert req.status_code == 200
    assert len(req.get_json()) == 1

def test_post():
    data = {
        'name':'Kotlin'
    }
    req = client.post('/api', json=data)
    assert req.status_code == 200
    assert req.get_json()[3]['name'] == data['name']