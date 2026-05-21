import sys
print("Python path:", sys.path)
try:
    from app.api.v1x import coins_db
    print("coins_db imported successfully")
    print("router:", coins_db.router)
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()