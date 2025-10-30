# Perplexity CLI

A command-line wrapper and GUI application for interacting with the Perplexity AI API.
Features both terminal and graphical interfaces with animated text output and code block rendering.

## Setup

1. **Clone & Install dependencies**

   ```bash
   git clone https://github.com/1ndevelopment/perplexity-cli
   cd perplexity-cli
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set your API key:**

   ```bash
   export PERPLEXITY_API_KEY="your_api_key_here"
   ```
   Or the script will prompt you to enter it when you run it.

## Usage

```bash
./ppx [-h] {search,chat} ...

Perplexity AI API Wrapper - Command Line Interface

positional arguments:
  {search,chat}  Available commands
    search       Perform a search query
    chat         Start a chat conversation

options:
  -h, --help     show this help message and exit

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
```
