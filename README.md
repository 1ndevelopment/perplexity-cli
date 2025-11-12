# Perplexity CLI

A command-line wrapper for interacting with the Perplexity AI API.

## Setup

1. **Clone & Install dependencies**

   ```bash
   git clone https://github.com/1ndevelopment/perplexity-cli
   cd perplexity-cli
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set your API key**

   ```bash
   export PERPLEXITY_API_KEY="your_api_key_here"
   ```
   Or the script will prompt you to enter it when you run it.

3. **Symlink ppx**

   ```bash
   sudo ln -s /path/to/perplexity-cli/ppx /usr/local/bin/ppx
   ```

## Usage

```bash
ppx [-h] {search,chat} ...

Perplexity AI API Wrapper - Command Line Interface

positional arguments:
  {search,chat}  Available commands
    search       Perform a search query
    chat         Start a chat conversation

options:
  -h, --help     show this help message and exit

Examples:
  # Simple search query
  ppx search "What is the latest news about AI?"

  # Chat conversation
  ppx chat "Hello, how are you?"

  # Use specific model
  ppx search "Explain quantum computing" --model llama-3.1-sonar-large-128k-chat

  # JSON output format
  ppx search "What is Python?" --format json

  # Custom parameters
  ppx search "Write a poem" --max-tokens 500 --temperature 0.8
```
