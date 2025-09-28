# test_imports.py
print("1. Testing basic imports...")
try:
    from src.config import settings
    print("✅ Settings OK")
except Exception as e:
    print(f"❌ Settings failed: {e}")

print("2. Testing models...")
try:
    from src.models import BaseResponse
    print("✅ Models OK")
except Exception as e:
    print(f"❌ Models failed: {e}")

print("3. Testing services...")
try:
    from src.services.content import content_service
    print("✅ Content service OK")
except Exception as e:
    print(f"❌ Content service failed: {e}")

print("4. Testing API creation...")
try:
    from src.api import create_app
    app = create_app()
    print("✅ App creation OK")
except Exception as e:
    print(f"❌ App creation failed: {e}")

print("5. Testing reels endpoint...")
try:
    from src.api.endpoints.reels import router
    print("✅ Reels router OK")
except Exception as e:
    print(f"❌ Reels router failed: {e}")

print("\n🎯 All tests completed!")