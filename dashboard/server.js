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