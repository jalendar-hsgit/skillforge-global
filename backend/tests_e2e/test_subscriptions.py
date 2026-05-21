import types
from app.services.stripe_service import stripe_service


def test_subscription_flow(client, login):
    c = login(email="sub@example.com", password="pass123")

    # plans
    r = c.get('/api/v1x/subscriptions/plans')
    assert r.status_code == 200

    # current
    r = c.get('/api/v1x/subscriptions/current')
    assert r.status_code == 200

    # stub stripe
    stripe_service.create_subscription = types.MethodType(lambda self, **kwargs: {
        'id': 'sub_test_123',
        'customer': 'cus_test_123',
        'status': 'active',
        'current_period_start': 1700000000,
        'current_period_end': 1702592000,
    }, stripe_service)
    stripe_service.cancel_subscription = types.MethodType(lambda self, **kwargs: True, stripe_service)

    # subscribe
    r = c.post('/api/v1x/subscriptions/subscribe', json={
        'plan': 'pro',
        'payment_method_id': 'pm_test_visa',
        'billing_cycle': 'monthly'
    })
    assert r.status_code == 201

    # cancel at period end
    r = c.post('/api/v1x/subscriptions/cancel', json={'cancel_immediately': False})
    assert r.status_code == 200
