# Perplexity CLI

A command-line wrapper and GUI application for interacting with the Perplexity AI API.
Features both terminal and graphical interfaces with animated text output and code block rendering.

## Features

- 🔍 **Search queries** - Ask questions and get real-time information
- 💬 **Chat conversations** - Interactive chat with the AI
- 🎨 **Pretty terminal output** - Formatted responses with emojis and structure
- 🖥️ **Modern GUI** - PyQt6-based graphical interface with animated text
- 📝 **Code block rendering** - Automatic detection and syntax highlighting for code
- ⚙️ **Customizable parameters** - Control model, temperature, max tokens
- 📊 **Usage statistics** - See token consumption
- 🔧 **Multiple output formats** - Pretty or JSON output

## Setup

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export PERPLEXITY_API_KEY="your_api_key_here"
   ```
   
   Or the script will prompt you to enter it when you run it.

3. **Make the script executable:**
   ```bash
   chmod +x wrapper.py
   ```

## Usage

### GUI Application (Recommended)
```bash
python run_gui.py
```
or
```bash
python gui.py
```

The GUI provides:
- 🎬 **Animated text output** - Characters appear with typing animation
- 📦 **Code block rendering** - Automatic detection and syntax highlighting
- 🎨 **Dark theme** - Modern, easy-on-the-eyes interface
- 💬 **Conversation history** - Maintains context across messages
- ⚙️ **Settings panel** - Easy API key management

### Command Line Interface

#### Basic Search
```bash
python wrapper.py search "What is the latest news about AI?"
```

#### Chat Conversation
```bash
python wrapper.py chat "Hello, how are you?"
```

### Advanced Options
```bash
# Use a different model
python wrapper.py search "Explain quantum computing" --model llama-3.1-sonar-large-128k-online

# JSON output format
python wrapper.py search "What is Python?" --format json

# Custom parameters
python wrapper.py search "Write a poem" --max-tokens 500 --temperature 0.8
```

## Available Models

- `sonar-pro` (default)
- `llama-3.1-sonar-small-128k-chat`
- `llama-3.1-sonar-large-128k-chat`
- `llama-3.1-sonar-huge-128k-chat`

## Command Line Options

### Search Command
- `query` - The search query to send to Perplexity AI
- `--model` - AI model to use (default: sonar-pro)
- `--max-tokens` - Maximum tokens in response (default: 1000)
- `--temperature` - Temperature for response generation (default: 0.2)
- `--format` - Output format: pretty or json (default: pretty)

### Chat Command
- `message` - The chat message to send
- Same options as search command

## Examples

```bash
# Quick information lookup
python wrapper.py search "What is the weather like today?"

# Technical explanation
python wrapper.py search "How does machine learning work?" --model llama-3.1-sonar-large-128k-online

# Creative writing
python wrapper.py chat "Write a short story about a robot" --temperature 0.8 --max-tokens 800

# Get structured data
python wrapper.py search "List the top 5 programming languages" --format json
```

## Environment Variables

- `PERPLEXITY_API_KEY` - Your Perplexity AI API key (required)

## Error Handling

The script includes comprehensive error handling:
- Invalid API keys
- Network connectivity issues
- API rate limits
- Malformed responses

## Output Format

The script provides beautifully formatted terminal output with:
- 🤖 Response indicators
- 📝 Content sections
- 📊 Token usage statistics
- 🏁 Completion status
- ❌ Error messages when needed
