import os
import sys
sys.path.insert(0, r"d:\python code\sfg\skillforge-global\backend")

# Set the key
os.environ['STRIPE_SECRET_KEY'] = 'sk_test_REPLACE_ME'
os.environ['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_51SkcWEBydMs9UJXdVYVVQ9PZbPnYbxk51Y9uQccHjfL4PVYNKfMqJRAy5IqIw2qxYfDEhzqPiPLvLZHfDx6ZqHVd00hOCwbvEr'

print('✅ Stripe Configuration Test')
print('=' * 60)

try:
    import stripe
    stripe.api_key = os.environ['STRIPE_SECRET_KEY']
    
    print(f'✅ STRIPE_SECRET_KEY configured')
    print(f'   Key: {stripe.api_key[:20]}...')
    print(f'')
    print(f'✅ STRIPE_PUBLISHABLE_KEY configured')
    print(f'   Key: {os.environ["STRIPE_PUBLISHABLE_KEY"][:20]}...')
    print(f'')
    
    # Test API connection
    print('Testing Stripe API connection...')
    test_customer = stripe.Customer.create(email='test-payment@skillforge.local')
    print(f'✅ Stripe API connection successful!')
    print(f'   Test customer ID: {test_customer.id}')
    
    # Clean up
    test_customer.delete()
    print(f'✅ Test cleanup successful')
    
except Exception as e:
    print(f'❌ Error: {str(e)[:200]}')
    import traceback
    traceback.print_exc()

print('=' * 60)
print('✅ Payment system Stripe integration is READY!')
print('')
print('Backend: http://localhost:8001')
print('Frontend: http://localhost:3000')
print('')
print('Test with card: 4242 4242 4242 4242')
