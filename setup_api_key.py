#!/usr/bin/env python3
"""
Helper script to set up Perplexity API key
"""

import os
import subprocess
import sys
import getpass

def setup_api_key():
    print("🔑 Perplexity API Key Setup")
    print("=" * 40)
    
    # Check if already set
    current_key = os.getenv("PERPLEXITY_API_KEY")
    if current_key:
        print(f"✅ API Key already set: {current_key[:10]}...{current_key[-4:]}")
        choice = input("Do you want to update it? (y/n): ").lower().strip()
        if choice != 'y':
            return
    
    # Get new API key
    print("\n📝 Enter your Perplexity API key:")
    print("   (You can find it at: https://www.perplexity.ai/settings/api)")
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Validate format
    if not api_key.startswith("pplx-"):
        print("⚠️  Warning: API key doesn't start with 'pplx-'. Are you sure this is correct?")
        confirm = input("Continue anyway? (y/n): ").lower().strip()
        if confirm != 'y':
            return
    
    # Set environment variable for current session
    os.environ["PERPLEXITY_API_KEY"] = api_key
    print(f"✅ API key set for current session: {api_key[:10]}...{api_key[-4:]}")
    
    # Offer to add to shell profile
    shell_profile = None
    if os.path.exists(os.path.expanduser("~/.bashrc")):
        shell_profile = "~/.bashrc"
    elif os.path.exists(os.path.expanduser("~/.zshrc")):
        shell_profile = "~/.zshrc"
    elif os.path.exists(os.path.expanduser("~/.profile")):
        shell_profile = "~/.profile"
    
    if shell_profile:
        print(f"\n💾 Add to {shell_profile} for permanent setup?")
        choice = input("(y/n): ").lower().strip()
        if choice == 'y':
            export_line = f'export PERPLEXITY_API_KEY="{api_key}"'
            profile_path = os.path.expanduser(shell_profile)
            
            # Check if already exists
            try:
                with open(profile_path, 'r') as f:
                    content = f.read()
                if "PERPLEXITY_API_KEY" in content:
                    print("⚠️  PERPLEXITY_API_KEY already exists in profile file")
                    return
            except:
                pass
            
            # Add to profile
            try:
                with open(profile_path, 'a') as f:
                    f.write(f"\n# Perplexity API Key\n{export_line}\n")
                print(f"✅ Added to {shell_profile}")
                print("🔄 Run 'source {shell_profile}' or restart your terminal to apply changes")
            except Exception as e:
                print(f"❌ Failed to write to {shell_profile}: {e}")
    
    # Test the API key
    print("\n🧪 Testing API key...")
    try:
        import requests
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ API key is working!")
        else:
            print(f"❌ API test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    setup_api_key()