import json
import types

from app.services.stripe_service import stripe_service


def test_subscription_plans_and_flow(client, login):
    # login test user
    c = login(email="sub@example.com", password="pass123")

    # get plans
    r = c.get('/api/v1x/subscriptions/plans')
    assert r.status_code == 200
    plans = r.json()
    assert any(p['plan'] == 'PRO' for p in plans)

    # current subscription (auto-created free)
    r = c.get('/api/v1x/subscriptions/current')
    assert r.status_code == 200
    cur = r.json()
    assert cur['plan'] in ('FREE', 'PRO', 'ENTERPRISE')

    # monkeypatch stripe create/cancel to avoid network
    def _fake_create_subscription(user_id, email, payment_method_id, plan, price_cents, billing_cycle='monthly'):
        return {
            'id': 'sub_test_123',
            'customer': 'cus_test_123',
            'status': 'active',
            'current_period_start': 1700000000,
            'current_period_end': 1702592000,
        }
    def _fake_cancel_subscription(subscription_id, cancel_immediately=False):
        return True

    # Patch methods
    stripe_service.create_subscription = types.MethodType(lambda self, **kwargs: _fake_create_subscription(**kwargs), stripe_service)
    stripe_service.cancel_subscription = types.MethodType(lambda self, **kwargs: _fake_cancel_subscription(**kwargs), stripe_service)

    # subscribe to PRO
    r = c.post('/api/v1x/subscriptions/subscribe', json={
        'plan': 'PRO',
        'payment_method_id': 'pm_test_visa',
        'billing_cycle': 'monthly'
    })
    assert r.status_code == 201
    sub = r.json()
    assert sub['plan'] == 'PRO'
    assert sub['status'] in ('ACTIVE', 'active', 'PAST_DUE', 'CANCELLED')

    # cancel at period end
    r = c.post('/api/v1x/subscriptions/cancel', json={ 'cancel_immediately': False })
    assert r.status_code == 200
    after = r.json()
    assert after.get('cancel_at_period_end') is True
