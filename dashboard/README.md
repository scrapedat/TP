
 # Ollama Tool Protocol Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)

A plug-and-play dashboard for managing, running, and customizing tools that integrate with Ollama models. This dashboard provides a comprehensive interface for tool discovery, execution, customization, and workflow management with a clean, modern UI.

## ✨ Features

- 🔧 **Dynamic Tool Registry**: JSON-based tool discovery and configuration
- 🚀 **Multi-Language Support**: Python, Node.js, and extensible architecture
- 🎯 **Real-Time Execution**: Execute tools with live feedback and results
- 🔗 **Ollama Integration**: Seamless integration with local Ollama models
- 👥 **Multi-Agent Support**: CrewAI and Swarm intelligence tools included
- 🎨 **Modern UI**: Clean, responsive dashboard with tool management
- 📊 **Analytics**: Execution history and performance tracking
- 🛠️ **Plugin Architecture**: Easy tool development and deployment

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Ollama running locally
- Git (for cloning)

### Installation

```bash
# 1. Clone or create the dashboard structure
mkdir -p ~/.ollama/dashboard
cd ~/.ollama/dashboard

# 2. Install dependencies
npm install express cors body-parser

# 3. Start the server
node server.js

# 4. Open the dashboard
# Option A: Open index.html directly in browser
# Option B: Visit http://localhost:3700 for served version
```

### Verify Installation
```bash
# Test API endpoint
curl http://localhost:3700/api/tools

# Should return your tool registry JSON
```

## 📁 Directory Structure

```
~/.ollama/dashboard/
├── index.html              # Main dashboard UI
├── server.js               # Express API server
├── package.json            # Node.js dependencies
├── config.json             # Dashboard configuration
├── tool-protocol-registry.json  # Tool definitions
├── ui-settings.json        # UI preferences
├── users.json              # User-specific settings
├── tools/                  # Tool scripts directory
│   ├── summarize.py        # Text summarization
│   ├── analyze.js          # Keyword analysis
│   ├── simple-crew.py      # Multi-agent orchestration
│   ├── simple-swarm.py     # Swarm intelligence
│   ├── ollama_client.py    # Shared Ollama client
│   └── crewai-adapter.py   # CrewAI integration
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── images/
└── docs/                   # Documentation
    ├── API.md
    ├── TOOL-DEVELOPMENT.md
    └── DEPLOYMENT.md
```

## 🛠️ Tool Development

### Adding a New Tool

1. **Create the script** in `tools/` directory:

```python
#!/usr/bin/env python3
import sys
import json

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        # Your tool logic here
        result = process_data(input_data)
        
        # Output JSON result
        print(json.dumps({
            "success": True,
            "result": result,
            "tool": "your_tool_name"
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "tool": "your_tool_name"
        }))

if __name__ == "__main__":
    main()
```

2. **Register in tool-protocol-registry.json**:

```json
{
  "id": "your_tool_id",
  "name": "Your Tool Name",
  "description": "Description of what your tool does",
  "script": "./tools/your_tool.py",
  "type": "python",
  "parameters": ["param1", "param2"],
  "features": ["feature1", "feature2"],
  "dependencies": ["ollama_client"],
  "category": "analysis",
  "tags": ["ai", "processing"]
}
```

3. **Test the tool**:

```bash
# Test via API
curl -X POST http://localhost:3700/api/run \
  -H "Content-Type: application/json" \
  -d '{"toolId": "your_tool_id", "params": {"param1": "value1"}}'
```

### Tool Development Guidelines

- **Input/Output**: Always use JSON for stdin/stdout communication
- **Error Handling**: Include try-catch blocks and meaningful error messages
- **Dependencies**: List all dependencies in the registry
- **Documentation**: Add clear descriptions and parameter documentation
- **Testing**: Test tools independently before registry integration

## 🔧 Configuration

### config.json
```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "default_model": "llama2"
  },
  "server": {
    "port": 3700,
    "cors_enabled": true
  },
  "tools": {
    "timeout": 60000,
    "max_buffer": "1MB",
    "auto_discovery": true
  }
}
```

### ui-settings.json
```json
{
  "theme": "light",
  "favorites": ["simple_crew", "summarize_py"],
  "pinned_tools": ["ollama_client"],
  "dashboard_layout": "grid",
  "show_advanced": false
}
```

## 🚀 Advanced Usage

### Tool Chaining
```javascript
// Chain multiple tools together
const pipeline = [
  { toolId: "summarize_py", params: { text: "..." } },
  { toolId: "analyze_js", params: { text: "{{previous.result}}" } }
];
```

### Batch Execution
```bash
# Execute multiple tools
curl -X POST http://localhost:3700/api/batch \
  -H "Content-Type: application/json" \
  -d '{"tools": [{"toolId": "tool1", "params": {}}, {"toolId": "tool2", "params": {}}]}'
```

### Custom Workflows
```json
{
  "workflow_id": "content_pipeline",
  "name": "Content Analysis Pipeline",
  "steps": [
    {"tool": "web_scraper", "params": {"url": "{{input.url}}"}},
    {"tool": "summarize_py", "params": {"text": "{{step1.content}}"}},
    {"tool": "analyze_js", "params": {"text": "{{step2.summary}}"}}
  ]
}
```

## 📚 Built-in Tools

| Tool | Type | Description | Parameters |
|------|------|-------------|------------|
| `summarize_py` | Python | Text summarization using AI | `text` |
| `analyze_js` | Node.js | Keyword extraction and analysis | `text` |
| `simple_crew` | Python | Multi-agent task orchestration | `task`, `agents`, `model` |
| `simple_swarm` | Python | Distributed processing with consensus | `task`, `swarm_size`, `models` |
| `ollama_client` | Python | Base Ollama API client | None (utility) |
| `crewai_adapter` | Python | CrewAI framework integration | `task`, `agents_config` |

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-tool`
3. **Add your tool** following our development guidelines
4. **Test thoroughly** with various inputs and edge cases
5. **Submit a pull request** with clear description

### Tool Submission Checklist
- [ ] Tool follows JSON input/output protocol
- [ ] Proper error handling implemented
- [ ] Registry entry is complete and accurate
- [ ] Tool has been tested independently
- [ ] Documentation is clear and complete
- [ ] Dependencies are properly listed

## 🐛 Troubleshooting

### Common Issues

**Tool not found error**
```bash
# Verify tool is registered
curl http://localhost:3700/api/tools | grep "your_tool_id"
```

**Python script errors**
```bash
# Test script independently
echo '{"test": "data"}' | python3 tools/your_tool.py
```

**Node.js script errors**
```bash
# Test script independently  
echo '{"test": "data"}' | node tools/your_tool.js
```

**Ollama connection issues**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags
```

## 📋 API Reference

### GET /api/tools
Returns all registered tools from the registry.

### POST /api/run
Execute a specific tool with parameters.
```json
{
  "toolId": "string",
  "params": { "key": "value" }
}
```

### POST /api/batch
Execute multiple tools in sequence.

### GET /api/status
System health check and statistics.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for the amazing local AI platform
- [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent frameworks
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/scrapedat/TP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/scrapedat/TP/discussions)
- **Documentation**: [Wiki](https://github.com/scrapedat/TP/wiki)

---

**Special Thanks to all unmentioned human and AI contributors GPTOSS, CLAUDE Sonnet, Claude Opus, and Gemini**
 
 
# license 
***Open Source. MIT License.***
