import sys
sys.path.insert(0, 'D:\\python code\\sfg\\skillforge-global\\backend')

try:
    import app.api.v1x.session
    print('SUCCESS: Session module imported')
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
