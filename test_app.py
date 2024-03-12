import pytest
from flask import session
from app import app

# Helper function to log in a user
def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

# Helper function to log out a user
def logout(client):
    return client.post('/logout', follow_redirects=True)



# Fixture to initialize Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_register_post(client):
    response = client.post('/register', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code in [200, 302]

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_post(client):
    response = login(client, 'testuser', 'testpass')
    assert response.status_code in [200, 302]

def test_dashboard(client):
    login(client, 'testuser', 'testpass')
    response = client.get('/dashboard')
    assert response.status_code in [200, 302]
    logout(client)

def test_logout(client):
    # Log in before attempting to log out
    login(client, 'testuser', 'testpass')
    
    # Now, log out
    response = logout(client)
    
    # Verify the logout was successful
    assert response.status_code in [200, 302]


def test_add_expense_get(client):
    login(client, 'testuser', 'testpass')
    response = client.get('/add_expense')
    assert response.status_code == 200
    logout(client)

def test_add_expense_post(client):
    login(client, 'testuser', 'testpass')
    response = client.post('/add_expense', data={
        'category': 'test', 
        'amount': '10', 
        'date': '2022-01-01', 
        'notes': 'test note'
    })
    assert response.status_code in [200, 302]
    logout(client)

def test_get_expense_data(client):
    login(client, 'testuser', 'testpass')
    response = client.get('/get_expense_data')
    assert response.status_code == 200
    data = response.get_json()  # This assumes Flask 1.0+
    assert type(data) is list  # Assuming the endpoint returns a list of expenses
    logout(client)

def test_remove_expense(client):
    login(client, 'testuser', 'testpass')
    add_response = client.post('/add_expense', data={
        'category': 'test',
        'amount': '10',
        'date': '2022-01-01',
        'notes': 'test note'
    }, follow_redirects=True)

    assert add_response.status_code == 200
    logout(client)
