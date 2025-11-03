import requests
import json

def test_compliance():
    url = "https://web-production-a4d44.up.railway.app/a2a/agent/codeHelper"
    
    test_cases = [
        {
            "message": "help",
            "channel_id": "test-channel",
            "user_id": "test-user"
        },
        {
            "message": "explain OOP",
            "channel_id": "test-channel", 
            "user_id": "test-user"
        }
    ]
    
    for i, test_data in enumerate(test_cases):
        print(f"Test {i+1}: {test_data['message']}")
        try:
            response = requests.post(url, json=test_data, timeout=10)
            data = response.json()
            
            # Check required fields
            required_fields = ['response', 'channel_id', 'user_id', 'agent', 'timestamp']
            missing = [field for field in required_fields if field not in data]
            
            if not missing:
                print("✅ A2A Compliant")
                print(f"Response: {data['response'][:100]}...")
            else:
                print(f"❌ Missing fields: {missing}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

test_compliance()