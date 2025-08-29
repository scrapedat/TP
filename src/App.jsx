import React, { useState, useEffect, useRef } from 'react';
import DataListsPanel from './components/DataListsPanel';
import CommunicationPanel from './components/CommunicationPanel';
import BrowserControlPanel from './components/BrowserControlPanel';
import ToolBuilder from './components/ToolBuilder';
import ModelManager from './components/ModelManager';

// --- Helper Components & Icons ---

// A simple loading spinner with a retro twist
const Spinner = () => (
  <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
);

// SVG Icons styled for the theme
const ToolIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
);
const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
);
const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 mr-2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
);

// --- Global Styles & Fonts ---

// Injects the retro font and CRT scanline effect into the document head
const CyberpunkStyles = () => {
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
      
      .font-orbitron {
        font-family: 'Orbitron', sans-serif;
      }

      .scanlines::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: repeating-linear-gradient(
          0deg,
          rgba(0, 0, 0, 0) 0,
          rgba(0, 0, 0, 0.4) 1px,
          rgba(0, 0, 0, 0) 2px
        );
        pointer-events: none;
        z-index: 9999;
        animation: scanline-flicker 0.1s infinite;
      }
      
      @keyframes scanline-flicker {
        0% { opacity: 0.9; }
        50% { opacity: 1; }
        100% { opacity: 0.9; }
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  return null;
};


// --- Panel Button Component ---
const PanelButton = ({ icon, label, active, onClick, color }) => {
  const colorClasses = {
    cyan: active ? 'bg-cyan-500 text-black' : 'text-cyan-400 hover:bg-cyan-900/30',
    fuchsia: active ? 'bg-fuchsia-500 text-black' : 'text-fuchsia-400 hover:bg-fuchsia-900/30',
    green: active ? 'bg-green-500 text-black' : 'text-green-400 hover:bg-green-900/30'
  };

  return (
    <button
      onClick={onClick}
      className={`w-12 h-12 mb-2 rounded-lg flex flex-col items-center justify-center transition-all ${colorClasses[color]} ${
        active ? 'shadow-lg' : ''
      }`}
      title={label}
    >
      <span className="text-lg">{icon}</span>
      <span className="text-xs mt-1">{label}</span>
    </button>
  );
};

// --- Main App Component ---

function App() {
  // --- State Management ---
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "SYSTEM ONLINE. AWAITING COMMANDS, OPERATOR." }
  ]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [model, setModel] = useState('llama3');
  const [isToolbeltVisible, setIsToolbeltVisible] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activePanel, setActivePanel] = useState('chat'); // 'chat', 'data', 'communication', 'browser'
  const [allTools, setAllTools] = useState([
    {
      name: 'get_weather_data',
      description: 'Fetches current weather data for a specified metropolis.',
      parameters: {
        type: 'object',
        properties: { location: { type: 'string', description: 'The city and state, e.g., Neo-Tokyo, JP' } },
        required: ['location'],
      },
    },
  ]);
  const [selectedTools, setSelectedTools] = useState(['get_weather_data']);
  const messagesEndRef = useRef(null);

  // --- Effects ---
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // --- Core Functions ---
  const handleToolToggle = (toolName) => {
    setSelectedTools(prev => prev.includes(toolName) ? prev.filter(t => t !== toolName) : [...prev, toolName]);
  };

  const handleAddTool = (newTool) => {
    if (!newTool.name || !newTool.description || !newTool.parameters) {
      alert("ERROR: ALL TOOL REGISTRATION FIELDS ARE MANDATORY.");
      return;
    }
    try {
      const parsedParams = JSON.parse(newTool.parameters);
      setAllTools(prev => [...prev, { ...newTool, parameters: parsedParams }]);
      setIsModalOpen(false);
    } catch {
      alert("ERROR: PARAMETER JSON SYNTAX CORRUPTED. ABORTING.");
    }
  };

  const generateSystemPrompt = () => {
    const activeTools = allTools.filter(t => selectedTools.includes(t.name));
    if (activeTools.length === 0) return "You are a helpful assistant.";
    const toolDefinitions = JSON.stringify(activeTools.map(t => ({
        type: 'function',
        function: { name: t.name, description: t.description, parameters: t.parameters }
    })), null, 2);
    return `You are a helpful assistant with access to the following tools.\n\nHere are the available tools:\n${toolDefinitions}\n\nWhen you need to call a tool, respond with a JSON object with a "tool_calls" key.`;
  };

  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading) return;
    const newMessages = [...messages, { role: 'user', content: userInput }];
    setMessages(newMessages);
    setUserInput('');
    setIsLoading(true);

    const requestBody = {
      model: model,
      messages: [{ role: 'system', content: generateSystemPrompt() }, ...newMessages.slice(-10)],
      stream: false,
      format: 'json',
    };

    try {
      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      if (!response.ok) throw new Error(`API response error: ${response.status}`);
      const data = await response.json();
      const responseContent = data.message.content;
      let finalResponse;
      try {
        const parsedContent = JSON.parse(responseContent);
        finalResponse = parsedContent.tool_calls
          ? { role: 'assistant', content: `// INITIATING TOOL PROTOCOL...`, toolCall: JSON.stringify(parsedContent.tool_calls, null, 2) }
          : { role: 'assistant', content: responseContent };
      } catch {
        finalResponse = { role: 'assistant', content: responseContent };
      }
      setMessages(prev => [...prev, finalResponse]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `// CONNECTION FAILED: UNABLE TO JACK INTO OLLAMA. CHECK LOCAL HOST.\n\n[${error.message}]` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <CyberpunkStyles />
      <div className="font-orbitron bg-black text-cyan-400 flex h-screen scanlines">
        {/* --- Panel Navigation --- */}
        <nav className="w-16 bg-black/90 border-r border-cyan-500 flex flex-col items-center py-4">
          <PanelButton
            icon="💬"
            label="CHAT"
            active={activePanel === 'chat'}
            onClick={() => setActivePanel('chat')}
            color="cyan"
          />
          <PanelButton
            icon="📊"
            label="DATA"
            active={activePanel === 'data'}
            onClick={() => setActivePanel('data')}
            color="cyan"
          />
          <PanelButton
            icon="📧"
            label="COMM"
            active={activePanel === 'communication'}
            onClick={() => setActivePanel('communication')}
            color="fuchsia"
          />
          <PanelButton
            icon="🌐"
            label="BROWSER"
            active={activePanel === 'browser'}
            onClick={() => setActivePanel('browser')}
            color="green"
          />
          <PanelButton
            icon="🔧"
            label="BUILDER"
            active={activePanel === 'builder'}
            onClick={() => setActivePanel('builder')}
            color="yellow"
          />
          <PanelButton
            icon="🤖"
            label="MODELS"
            active={activePanel === 'models'}
            onClick={() => setActivePanel('models')}
            color="purple"
          />
        </nav>

        {/* --- Main Content Area --- */}
        <main className="flex-1 flex flex-col bg-black bg-opacity-80 border-r-2 border-fuchsia-500 shadow-[0_0_15px_rgba(217,70,239,0.5)]">
          {/* Chat Panel */}
          {activePanel === 'chat' && (
            <>
              <header className="p-4 flex justify-between items-center border-b-2 border-fuchsia-500 bg-black/50">
                <h1 className="text-xl font-bold text-fuchsia-500 animate-pulse">OLLAMA CORTEX INTERFACE</h1>
                <div className="flex items-center space-x-4">
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="bg-black border-2 border-cyan-400 rounded-none px-2 py-1 text-cyan-400 focus:outline-none focus:shadow-[0_0_10px_rgba(34,211,238,0.7)]"
                  >
                    <option>llama3</option><option>phi3</option><option>mistral</option>
                  </select>
                  <button
                    onClick={() => setIsToolbeltVisible(!isToolbeltVisible)}
                    className="p-2 border-2 border-cyan-400 hover:bg-cyan-400 hover:text-black transition-colors"
                    title="Toggle Toolbelt"
                  >
                    <ToolIcon />
                  </button>
                </div>
              </header>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((msg, index) => (
                  <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xl lg:max-w-2xl px-5 py-3 ${msg.role === 'user' ? 'bg-fuchsia-900/50 border-2 border-fuchsia-500' : 'bg-cyan-900/50 border-2 border-cyan-400'}`}>
                      <p className="whitespace-pre-wrap" style={{ textShadow: '0 0 5px currentColor' }}>{msg.content}</p>
                      {msg.toolCall && (
                        <pre className="mt-2 bg-black/70 text-lime-400 p-3 text-sm overflow-x-auto border-2 border-lime-400">
                          <code>{msg.toolCall}</code>
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t-2 border-fuchsia-500 bg-black/50">
                <div className="relative max-w-4xl mx-auto">
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                    placeholder="EXECUTE COMMAND..."
                    className="w-full bg-black border-2 border-cyan-400 rounded-none p-3 pr-20 resize-none focus:outline-none focus:shadow-[0_0_10px_rgba(34,211,238,0.7)] text-cyan-400 placeholder-cyan-700"
                    rows={1}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-cyan-400 text-black disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? <Spinner /> : <SendIcon />}
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Data Management Panel */}
          {activePanel === 'data' && <DataListsPanel />}

          {/* Communication Panel */}
          {activePanel === 'communication' && <CommunicationPanel />}

          {/* Browser Control Panel */}
          {activePanel === 'browser' && <BrowserControlPanel />}

          {/* Tool Builder Panel */}
          {activePanel === 'builder' && <ToolBuilder />}

          {/* Model Manager Panel */}
          {activePanel === 'models' && <ModelManager />}
        </main>

        {/* --- Toolbelt Sidebar (Chat Panel Only) --- */}
        {activePanel === 'chat' && (
          <aside className={`bg-black/80 flex flex-col transition-all duration-300 ${isToolbeltVisible ? 'w-80' : 'w-0'}`} style={{ overflow: 'hidden' }}>
          <div className="p-4 border-b-2 border-fuchsia-500">
            <h2 className="text-lg font-semibold text-fuchsia-500">TOOLBELT_</h2>
          </div>
          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {allTools.map(tool => (
              <div key={tool.name} className="bg-cyan-900/50 p-3 border-2 border-cyan-400">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="font-medium text-cyan-400">{tool.name}</span>
                  <input
                    type="checkbox"
                    checked={selectedTools.includes(tool.name)}
                    onChange={() => handleToolToggle(tool.name)}
                    className="h-5 w-5 appearance-none border-2 border-fuchsia-500 checked:bg-fuchsia-500"
                  />
                </label>
                <p className="text-xs text-cyan-600 mt-1">{tool.description}</p>
              </div>
            ))}
          </div>
          <div className="p-4 border-t-2 border-fuchsia-500">
            <button
              onClick={() => setIsModalOpen(true)}
              className="w-full flex items-center justify-center bg-fuchsia-500 hover:bg-fuchsia-400 text-black font-bold py-2 px-4 transition-colors"
            >
              <PlusIcon />
              FABRICATE TOOL
            </button>
          </div>
          </aside>
        )}

        {/* --- New Tool Modal (Chat Panel Only) --- */}
        {activePanel === 'chat' && isModalOpen && (
          <CreateToolModal onClose={() => setIsModalOpen(false)} onAddTool={handleAddTool} />
        )}
      </div>
    </>
  );
}

// --- Modal Component for Creating Tools ---
const CreateToolModal = ({ onClose, onAddTool }) => {
  const [toolName, setToolName] = useState('');
  const [toolDescription, setToolDescription] = useState('');
  const [toolParams, setToolParams] = useState(JSON.stringify({
    type: 'object',
    properties: { param1: { type: 'string', description: 'Description' } },
    required: ['param1'],
  }, null, 2));
  
  const handleSubmit = () => onAddTool({ name: toolName, description: toolDescription, parameters: toolParams });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 font-orbitron">
      <div className="bg-black border-2 border-fuchsia-500 shadow-[0_0_20px_rgba(217,70,239,0.6)] p-6 w-full max-w-lg mx-4">
        <h2 className="text-2xl font-bold mb-4 text-fuchsia-500">NEW TOOL FABRICATION</h2>
        <div className="space-y-4">
          <input
            type="text" value={toolName} onChange={(e) => setToolName(e.target.value)}
            placeholder="Tool Codename..."
            className="w-full bg-black border-2 border-cyan-400 rounded-none p-2 focus:outline-none focus:shadow-[0_0_10px_rgba(34,211,238,0.7)] text-cyan-400"
          />
          <input
            type="text" value={toolDescription} onChange={(e) => setToolDescription(e.target.value)}
            placeholder="Function Description..."
            className="w-full bg-black border-2 border-cyan-400 rounded-none p-2 focus:outline-none focus:shadow-[0_0_10px_rgba(34,211,238,0.7)] text-cyan-400"
          />
          <textarea
            value={toolParams} onChange={(e) => setToolParams(e.target.value)}
            className="w-full bg-black font-mono text-sm border-2 border-cyan-400 rounded-none p-2 h-48 resize-y focus:outline-none focus:shadow-[0_0_10px_rgba(34,211,238,0.7)] text-cyan-400"
          />
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <button onClick={onClose} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-semibold">CANCEL</button>
          <button onClick={handleSubmit} className="px-4 py-2 bg-cyan-400 hover:bg-cyan-300 text-black font-semibold">FABRICATE</button>
        </div>
      </div>
    </div>
  );
};

export default App;
