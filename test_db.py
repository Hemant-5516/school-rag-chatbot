from app.db_utils import test_connection

success, result = test_connection()
if success:
    print("Connection successful! Tables found:", result)
else:
    print("Connection failed:", result)