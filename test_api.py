#!/usr/bin/env python3
"""
Simple test script to debug Perplexity API connection
"""

import os
import requests
import json

def test_perplexity_api():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ PERPLEXITY_API_KEY environment variable not found")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test message."
            }
        ],
        "max_tokens": 100
    }
    
    print(f"🌐 URL: {url}")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API connection successful!")
        else:
            print("❌ API connection failed")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_perplexity_api()