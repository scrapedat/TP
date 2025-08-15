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