# TP
Tool Protocol Dashboard - easy user interface for ollama tool calling - ollama and human interface to set tools, rules, tools rules, and rules for tools. 
````markdown name=OLLAMA-TP-DASHBOARD-STRUCTURE.md
# Ollama Tool Protocol Dashboard — Starter File Structure

Copy this structure into your ~/.ollama/dashboard/ directory.  
This is a minimal, working starter for a TP dashboard with sample tools.

## Directory Layout

```
~/.ollama/
├── models/
│   └── GPToss:20b/
│       ├── model.json
│       └── tool-scripts/
│           ├── summarize.py
│           └── analyze.js
└── dashboard/
    ├── config.json
    ├── tool-protocol-registry.json
    ├── users.json
    ├── ui-settings.json
    ├── tools/
    │   ├── summarize.py
    │   └── analyze.js
    ├── sample-tools.json
    ├── package.json
    ├── server.js
    ├── index.html
    └── README.md
```

## Key Files

- **config.json** — Dashboard config, e.g. Ollama model path.
- **tool-protocol-registry.json** — Registered tools (UI sees these).
- **users.json** — (Optional) User data.
- **ui-settings.json** — UI preferences (theme, favorites, pins).
- **tools/** — Drop-in Node/Python tool scripts.
- **sample-tools.json** — For UI or import.
- **server.js** — Minimal Node API server for tool execution.
- **package.json** — Node dependencies.
- **index.html** — Minimal dashboard UI (works with server.js).
- **README.md** — Quickstart & help.

## How to Use

1. Place this structure in `~/.ollama/dashboard/`
2. Run `npm install` inside `dashboard/`
3. Run `node server.js`
4. Open `index.html` for UI, or visit `http://localhost:3700/index.html` if serving statically
````

---

```json name=dashboard/config.json
{
  "ollama_models_path": "../models/",
  "default_model": "GPToss:20b",
  "tool_scripts_dir": "./tools/",
  "port": 3700,
  "enable_wishlist": true
}
```

```json name=dashboard/tool-protocol-registry.json
[
  {
    "id": "summarize_py",
    "name": "Summarize Text",
    "description": "Summarize a block of text using Python.",
    "script": "./tools/summarize.py",
    "type": "python",
    "parameters": ["text"],
    "isPinned": true,
    "isFavorite": true,
    "customLabel": "Summarizer"
  },
  {
    "id": "analyze_js",
    "name": "Keyword Analyzer",
    "description": "Extract keywords using Node.js.",
    "script": "./tools/analyze.js",
    "type": "nodejs",
    "parameters": ["text"],
    "isPinned": false,
    "isFavorite": false
  }
]
```

```json name=dashboard/sample-tools.json
[
  {
    "id": "summarize_py",
    "name": "Summarize Text",
    "description": "Summarize a block of text using Python.",
    "script": "./tools/summarize.py",
    "type": "python",
    "parameters": ["text"]
  },
  {
    "id": "analyze_js",
    "name": "Keyword Analyzer",
    "description": "Extract keywords using Node.js.",
    "script": "./tools/analyze.js",
    "type": "nodejs",
    "parameters": ["text"]
  }
]
```

```json name=dashboard/ui-settings.json
{
  "theme": "light",
  "favorites": ["summarize_py"],
  "pinned": ["summarize_py"],
  "toolOrder": ["summarize_py", "analyze_js"]
}
```

```json name=dashboard/users.json
[
  {
    "id": "default",
    "name": "First User",
    "preferences": {
      "theme": "light"
    },
    "lastLogin": "2025-08-15T10:41:01Z"
  }
]
```

```python name=dashboard/tools/summarize.py
import sys
import json

def summarize(text):
    # Very basic: just returns the first sentence.
    return text.split('.')[0] + '.'

if __name__ == "__main__":
    try:
        # Input from stdin as JSON
        input_data = json.load(sys.stdin)
        text = input_data.get("text", "")
        summary = summarize(text)
        print(json.dumps({"summary": summary}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
```

```javascript name=dashboard/tools/analyze.js
const readline = require('readline');

function extractKeywords(text) {
  // Simple: split by space, remove duplicates, sort by frequency
  const words = text.toLowerCase().match(/\w+/g) || [];
  const freq = {};
  words.forEach(w => freq[w] = (freq[w] || 0) + 1);
  return Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
}

const rl = readline.createInterface({ input: process.stdin });
let input = '';
rl.on('line', line => input += line);
rl.on('close', () => {
  try {
    const data = JSON.parse(input);
    const text = data.text || '';
    const keywords = extractKeywords(text);
    console.log(JSON.stringify({ keywords }));
  } catch (e) {
    console.log(JSON.stringify({ error: e.toString() }));
  }
});
```

```json name=dashboard/package.json
{
  "name": "ollama-tp-dashboard",
  "version": "1.0.0",
  "description": "Ollama Tool Protocol Dashboard - plug-and-play tool runner for Ollama models",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "body-parser": "^1.20.2"
  }
}
```

```javascript name=dashboard/server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const registryPath = path.join(__dirname, 'tool-protocol-registry.json');
const toolsDir = path.join(__dirname, 'tools');

function loadRegistry() {
  return JSON.parse(fs.readFileSync(registryPath));
}

app.get('/api/tools', (req, res) => {
  res.json(loadRegistry());
});

app.post('/api/run', (req, res) => {
  const { toolId, params } = req.body;
  const registry = loadRegistry();
  const tool = registry.find(t => t.id === toolId);
  if (!tool) return res.status(404).json({ error: "Tool not found" });

  const scriptPath = path.join(toolsDir, path.basename(tool.script));
  if (tool.type === "python") {
    const proc = execFile('python3', [scriptPath], { maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) return res.status(500).json({ error: stderr || err.message });
      try {
        res.json(JSON.parse(stdout));
      } catch {
        res.status(500).json({ error: "Tool returned invalid JSON" });
      }
    });
    proc.stdin.write(JSON.stringify(params));
    proc.stdin.end();
  } else if (tool.type === "nodejs") {
    const proc = execFile('node', [scriptPath], { maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) return res.status(500).json({ error: stderr || err.message });
      try {
        res.json(JSON.parse(stdout));
      } catch {
        res.status(500).json({ error: "Tool returned invalid JSON" });
      }
    });
    proc.stdin.write(JSON.stringify(params));
    proc.stdin.end();
  } else {
    res.status(400).json({ error: "Unknown tool type" });
  }
});

app.listen(3700, () => {
  console.log('Ollama TP Dashboard API running at http://localhost:3700');
});
```

```html name=dashboard/index.html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Ollama Tool Protocol Dashboard</title>
  <style>
    body { font-family: sans-serif; background: #fafbfc; padding: 2em; }
    .tool-card { border: 1px solid #eee; border-radius: 8px; padding: 1em; margin: 1em 0; background: #fff; }
    .tool-actions { float: right; }
    .execute-btn { background: #36c; color: #fff; border: none; border-radius: 4px; padding: 0.5em 1em; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Ollama Tool Protocol Dashboard</h1>
  <div id="tools"></div>
  <script>
    async function loadTools() {
      const res = await fetch('/api/tools');
      const tools = await res.json();
      const root = document.getElementById('tools');
      root.innerHTML = '';
      for (const tool of tools) {
        const card = document.createElement('div');
        card.className = 'tool-card';
        card.innerHTML = `<strong>${tool.customLabel || tool.name}</strong>
          <span class="tool-actions">
            <button class="execute-btn" data-id="${tool.id}">Run</button>
          </span>
          <br><small>${tool.description}</small>
          <pre id="output-${tool.id}"></pre>`;
        root.appendChild(card);
      }
      document.querySelectorAll('.execute-btn').forEach(btn => {
        btn.onclick = async () => {
          const toolId = btn.getAttribute('data-id');
          const input = prompt("Enter input text for the tool:");
          const res = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ toolId, params: { text: input } })
          });
          const out = await res.json();
          document.getElementById(`output-${toolId}`).textContent = JSON.stringify(out, null, 2);
        };
      });
    }
    loadTools();
  </script>
</body>
</html>
```

````markdown name=dashboard/README.md
# Ollama Tool Protocol Dashboard

A plug-and-play dashboard for managing, running, and customizing tools that integrate with Ollama models (e.g., GPToss:20b). This dashboard provides an interface for tool discovery, execution, customization, and wishlist management, all with a clean UI.

---

## Directory Structure

(see OLLAMA-TP-DASHBOARD-STRUCTURE.md for full layout)

---

## Quick Start

1. Place this structure in `~/.ollama/dashboard/`
2. Run `npm install` inside `dashboard/`
3. Run `node server.js`
4. Open `index.html` for UI, or visit `http://localhost:3700/index.html` if serving statically

---

## Adding or Editing Tools

- Drop Python or Node.js scripts in the `tools/` directory.
- Add an entry for the tool in `tool-protocol-registry.json` similar to the samples provided.

---

## Configuration

- **config.json**: Controls dashboard behavior and Ollama path.
- **tool-protocol-registry.json**: All registered tools.
- **ui-settings.json**: UI preferences, favorites, pins.
- **users.json**: Optional user-specific state.

---

## License

Open Source. MIT License.
````

```json name=dashboard/.gitignore
node_modules/
*.pyc
.DS_Store
.env
```
