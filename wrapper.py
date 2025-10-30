#!/usr/bin/env python3
"""
Perplexity AI API Wrapper Script
A command-line interface for interacting with Perplexity AI API
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, Any, Optional
import time
import getpass

class PerplexityWrapper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, 
                       messages: list, 
                       model: str = "sonar-pro",
                       max_tokens: int = 1000,
                       temperature: float = 0.2,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Send a chat completion request to Perplexity AI
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"].get("message", error_detail)
                except:
                    pass
                return {"error": f"HTTP {response.status_code}: {error_detail}"}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def search(self, query: str, model: str = "sonar-pro") -> Dict[str, Any]:
        """
        Perform a search query using Perplexity AI
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant that provides accurate and up-to-date information."
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        return self.chat_completion(messages, model=model)
    
    def format_output(self, response: Dict[str, Any], format_type: str = "pretty") -> str:
        """
        Format the API response for terminal output
        """
        if "error" in response:
            return f"❌ Error: {response['error']}"
        
        if format_type == "json":
            return json.dumps(response, indent=2)
        
        # Pretty format
        output = []
        output.append("🤖 Perplexity AI Response")
        output.append("=" * 50)
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            if "message" in choice:
                content = choice["message"].get("content", "No content")
                output.append(f"\n📝 Response:\n")
                output.append(content)
            
            if "finish_reason" in choice:
                output.append(f"\n🏁 Finish Reason: {choice['finish_reason']}")
        
        if "usage" in response:
            usage = response["usage"]
            output.append(f"\n📊 Token Usage:")
            output.append(f"  • Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            output.append(f"  • Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            output.append(f"  • Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        return "\n".join(output)
    

def get_api_key() -> Optional[str]:
    """
    Get API key from environment variable or prompt user
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY environment variable not found.")
        api_key = getpass.getpass("Enter your Perplexity API key: ").strip()
        if not api_key:
            print("❌ No API key provided. Exiting.")
            sys.exit(1)
    return api_key

def main():
    parser = argparse.ArgumentParser(
        description="Perplexity AI API Wrapper - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple search query
  python wrapper.py search "What is the latest news about AI?"

  # Chat conversation
  python wrapper.py chat "Hello, how are you?"

  # Use specific model
  python wrapper.py search "Explain quantum computing" --model llama-3.1-sonar-large-128k-chat

  # JSON output format
  python wrapper.py search "What is Python?" --format json

  # Custom parameters
  python wrapper.py search "Write a poem" --max-tokens 500 --temperature 0.8

        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Perform a search query")
    search_parser.add_argument("query", help="Search query")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start a chat conversation")
    chat_parser.add_argument("message", help="Chat message")
    
    # Common arguments
    for subparser in [search_parser, chat_parser]:
        subparser.add_argument("--model", 
                              default="sonar-pro",
                              help="Model to use (default: sonar-pro)")
        subparser.add_argument("--max-tokens", 
                              type=int, 
                              default=1000,
                              help="Maximum tokens in response (default: 1000)")
        subparser.add_argument("--temperature", 
                              type=float, 
                              default=0.2,
                              help="Temperature for response generation (default: 0.2)")
        subparser.add_argument("--format", 
                              choices=["pretty", "json"], 
                              default="pretty",
                              help="Output format (default: pretty)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Get API key
    api_key = get_api_key()
    
    # Initialize wrapper
    wrapper = PerplexityWrapper(api_key)
    
    # Execute command
    if args.command == "search":
        print(f"🔍 Searching: {args.query}")
        print("⏳ Please wait...")
        
        response = wrapper.search(
            query=args.query,
            model=args.model
        )
        
        output_text = wrapper.format_output(response, args.format)
        print("\n" + output_text)
    
    elif args.command == "chat":
        print(f"💬 Chat: {args.message}")
        print("⏳ Please wait...")
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": args.message
            }
        ]
        
        response = wrapper.chat_completion(
            messages=messages,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        
        output_text = wrapper.format_output(response, args.format)
        print("\n" + output_text)

if __name__ == "__main__":
    main()
