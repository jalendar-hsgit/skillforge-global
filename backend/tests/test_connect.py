import types
from app.services.stripe_service import stripe_service


def test_connect_account_flow(client, ensure_mentor):
    # Ensure mentor for test user
    mentor = ensure_mentor(email="connectmentor@example.com")

    # login as that mentor's user
    r = client.post('/api/v1/auth/login', json={'email': 'connectmentor@example.com', 'password': 'testpass'})
    assert r.status_code == 200

    # stub stripe calls
    stripe_service.create_connect_account = types.MethodType(lambda self, **kwargs: {'id': 'acct_test_123', 'payouts_enabled': False, 'details_submitted': False}, stripe_service)
    stripe_service.create_connect_onboarding_link = types.MethodType(lambda self, **kwargs: {'url': 'https://connect.stripe.com/onboarding/test'}, stripe_service)
    stripe_service.get_connect_account = types.MethodType(lambda self, account_id: {'id': account_id, 'payouts_enabled': False, 'details_submitted': False, 'requirements': {'currently_due': []}}, stripe_service)
    stripe_service.create_connect_login_link = types.MethodType(lambda self, account_id: {'url': 'https://dashboard.stripe.com/test'}, stripe_service)

    # create account
    r = client.post('/api/v1x/connect/create-account')
    assert r.status_code == 200
    assert r.json().get('account_id') == 'acct_test_123'

    # onboarding link
    r = client.get('/api/v1x/connect/onboarding-link')
    assert r.status_code == 200
    assert 'url' in r.json()

    # status
    r = client.get('/api/v1x/connect/status')
    assert r.status_code == 200
    body = r.json()
    assert body.get('account_id') == 'acct_test_123'

    # login link
    r = client.get('/api/v1x/connect/login-link')
    assert r.status_code == 200
    assert 'url' in r.json()
