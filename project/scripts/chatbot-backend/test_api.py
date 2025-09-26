import requests
import json
import uuid

# API Base URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Sağlık kontrolü testi"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("🔍 Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat(message, session_id=None):
    """Chat endpoint testi"""
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    try:
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        print(f"💬 Chat Test - Session: {session_id}")
        print(f"Message: {message}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Answer: {result['answer']}")
            print(f"Status: {result['status']}")
        else:
            print(f"❌ Error: {response.text}")
        
        print("-" * 50)
        return session_id
        
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        print("-" * 50)
        return session_id

def test_session_history(session_id):
    """Session geçmişi testi"""
    try:
        response = requests.get(f"{BASE_URL}/sessions/{session_id}/history")
        print(f"📜 Session History - Session: {session_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ History: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Session history test failed: {e}")
        print("-" * 50)

if __name__ == "__main__":
    print("🚀 FastAPI Backend Test Script")
    print("=" * 50)
    
    # 1. Health check
    if not test_health():
        print("❌ Backend server çalışmıyor! Lütfen start_server.bat ile başlatın.")
        exit(1)
    
    # 2. Chat testleri
    session_id = test_chat("Merhaba! Nasılsın?")
    test_chat("İstanbul'dan Ankara'ya uçmak istiyorum", session_id)
    test_chat("Yarın için uygun uçuşlar var mı?", session_id)
    
    # 3. Session geçmişi
    test_session_history(session_id)
    
    print("✅ Tüm testler tamamlandı!")