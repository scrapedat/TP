import React, { useState, useEffect } from 'react';

// Browser Control Panel
const BrowserControlPanel = () => {
  const [websites, setWebsites] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [screenshot, setScreenshot] = useState(null);
  const [credentials, setCredentials] = useState({});
  const [showCredentialModal, setShowCredentialModal] = useState(false);
  const [selectedWebsite, setSelectedWebsite] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [ollamaInstructions, setOllamaInstructions] = useState('');
  const [showPresetModal, setShowPresetModal] = useState(false);
  const [editingPreset, setEditingPreset] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Load websites, credentials, and sessions on component mount
  useEffect(() => {
    loadWebsites();
    loadCredentials();
    loadSessions();

    // Set up screenshot polling for active session
    const interval = setInterval(() => {
      if (activeSession) {
        updateScreenshot(activeSession.session_id);
      }
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [activeSession]);

  const loadWebsites = async () => {
    try {
      const response = await fetch('/api/presets');
      if (response.ok) {
        const data = await response.json();
        setWebsites(data.presets || []);
      } else {
        // Fallback to default websites if API fails
        setWebsites([
          { preset_id: 'default_1', name: 'Google', url: 'https://google.com', category: 'search', icon: '🔍' },
          { preset_id: 'default_2', name: 'Gmail', url: 'https://gmail.com', category: 'email', icon: '📧' },
          { preset_id: 'default_3', name: 'GitHub', url: 'https://github.com', category: 'development', icon: '💻' },
          { preset_id: 'default_4', name: 'YouTube', url: 'https://youtube.com', category: 'media', icon: '📺' }
        ]);
      }
    } catch (error) {
      console.error('Error loading websites:', error);
      // Fallback to default websites
      setWebsites([
        { preset_id: 'default_1', name: 'Google', url: 'https://google.com', category: 'search', icon: '🔍' },
        { preset_id: 'default_2', name: 'Gmail', url: 'https://gmail.com', category: 'email', icon: '📧' },
        { preset_id: 'default_3', name: 'GitHub', url: 'https://github.com', category: 'development', icon: '💻' },
        { preset_id: 'default_4', name: 'YouTube', url: 'https://youtube.com', category: 'media', icon: '📺' }
      ]);
    }
  };

  const loadCredentials = async () => {
    // Placeholder for stored credentials (in production, this would be encrypted)
    setCredentials({
      '1': { username: 'user@gmail.com', password: '••••••••' },
      '5': { username: 'developer', password: '••••••••' }
    });
  };

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/browser/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const createBrowserSession = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/browser/create_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'default' })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          await loadSessions();
          // Auto-select the new session
          const newSession = { session_id: data.session_id, status: 'ready' };
          setActiveSession(newSession);
        }
      }
    } catch (error) {
      console.error('Error creating session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const navigateSession = async (sessionId, url) => {
    try {
      const response = await fetch(`/api/browser/${sessionId}/navigate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.screenshot) {
          setScreenshot(data.screenshot);
        }
      }
    } catch (error) {
      console.error('Error navigating:', error);
    }
  };

  const executeBrowserAction = async (sessionId, action, parameters = {}) => {
    try {
      const response = await fetch(`/api/browser/${sessionId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, parameters })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.screenshot) {
          setScreenshot(data.screenshot);
        }
        return data;
      }
    } catch (error) {
      console.error('Error executing action:', error);
    }
    return null;
  };

  const updateScreenshot = async (sessionId) => {
    try {
      const response = await fetch(`/api/browser/${sessionId}/screenshot`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.screenshot) {
          setScreenshot(data.screenshot);
        }
      }
    } catch (error) {
      console.error('Error updating screenshot:', error);
    }
  };

  const toggleAIControl = async (sessionId, enable) => {
    try {
      const endpoint = enable ? 'enable_ai' : 'disable_ai';
      const response = await fetch(`/api/browser/${sessionId}/${endpoint}`, {
        method: 'POST'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setActiveSession(prev => ({ ...prev, ai_controlled: enable }));
        }
      }
    } catch (error) {
      console.error('Error toggling AI control:', error);
    }
  };

  const closeSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/browser/${sessionId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadSessions();
        if (activeSession?.session_id === sessionId) {
          setActiveSession(null);
          setScreenshot(null);
        }
      }
    } catch (error) {
      console.error('Error closing session:', error);
    }
  };

  const sendOllamaInstructions = async () => {
    if (!activeSession || !ollamaInstructions.trim()) return;

    // This would integrate with Ollama to send instructions
    console.log('Sending instructions to Ollama:', ollamaInstructions);

    // For now, just show the instructions were sent
    setOllamaInstructions('');
  };

  const startBrowserSession = async (website) => {
    setIsLoading(true);
    try {
      // Mark preset as used
      if (website.preset_id) {
        await markPresetUsed(website.preset_id);
      }

      // Try to create a real browser session first
      try {
        const response = await fetch('/api/browser/create_session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'default' })
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            // Navigate to the website
            const navResponse = await fetch(`/api/browser/${data.session_id}/navigate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url: website.url })
            });

            if (navResponse.ok) {
              const navData = await navResponse.json();
              setActiveSession({
                session_id: data.session_id,
                website: website,
                status: 'ready',
                ai_controlled: false,
                current_url: website.url
              });

              if (navData.screenshot) {
                setScreenshot(navData.screenshot);
              }
              setIsLoading(false);
              return;
            }
          }
        }
      } catch (error) {
        console.error('Real browser session failed, using simulation:', error);
      }

      // Fallback to simulation if real browser fails
      setActiveSession({
        session_id: `session_${Date.now()}`,
        website: website,
        status: 'connecting',
        ai_controlled: false,
        current_url: website.url
      });

      // Simulate taking screenshot
      setTimeout(() => {
        setScreenshot('/api/placeholder-screenshot.png'); // Placeholder
        setActiveSession(prev => ({ ...prev, status: 'ready' }));
        setIsLoading(false);
      }, 2000);

    } catch (error) {
      console.error('Error starting session:', error);
      setIsLoading(false);
    }
  };

  const stopBrowserSession = () => {
    setActiveSession(null);
    setScreenshot(null);
  };

  const saveCredentials = (websiteId, creds) => {
    setCredentials(prev => ({
      ...prev,
      [websiteId]: creds
    }));
    setShowCredentialModal(false);
  };

  const createPreset = async (presetData) => {
    try {
      const response = await fetch('/api/presets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(presetData)
      });

      if (response.ok) {
        const data = await response.json();
        await loadWebsites(); // Refresh the list
        return data;
      } else {
        throw new Error('Failed to create preset');
      }
    } catch (error) {
      console.error('Error creating preset:', error);
      throw error;
    }
  };

  const updatePreset = async (presetId, updates) => {
    try {
      const response = await fetch(`/api/presets/${presetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        const data = await response.json();
        await loadWebsites(); // Refresh the list
        return data;
      } else {
        throw new Error('Failed to update preset');
      }
    } catch (error) {
      console.error('Error updating preset:', error);
      throw error;
    }
  };

  const deletePreset = async (presetId) => {
    try {
      const response = await fetch(`/api/presets/${presetId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadWebsites(); // Refresh the list
        return true;
      } else {
        throw new Error('Failed to delete preset');
      }
    } catch (error) {
      console.error('Error deleting preset:', error);
      throw error;
    }
  };

  const markPresetUsed = async (presetId) => {
    try {
      await fetch(`/api/presets/${presetId}/use`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error marking preset as used:', error);
    }
  };

  const filteredWebsites = websites.filter(website =>
    website.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    website.url.toLowerCase().includes(searchQuery.toLowerCase()) ||
    website.category.toLowerCase().includes(searchQuery.toLowerCase())
  );



  const categories = [...new Set(filteredWebsites.map(w => w.category))];

  return (
    <div className="browser-control-panel bg-black/80 border-2 border-green-500 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-green-500">BROWSER CONTROL</h2>
        <div className="flex gap-2">
          <button
            onClick={createBrowserSession}
            disabled={isLoading}
            className="px-3 py-1 bg-green-500 text-black rounded hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'CREATING...' : 'NEW SESSION'}
          </button>
          {activeSession && (
            <button
              onClick={() => closeSession(activeSession.session_id)}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-500 transition-colors"
            >
              CLOSE SESSION
            </button>
          )}
        </div>
      </div>

      {/* Session Selection */}
      {sessions.length > 0 && (
        <div className="mb-4">
          <h3 className="text-green-400 font-medium mb-2">ACTIVE SESSIONS</h3>
          <div className="space-y-2">
            {sessions.map(session => (
              <div
                key={session.session_id}
                className={`p-2 border rounded cursor-pointer transition-all ${
                  activeSession?.session_id === session.session_id
                    ? 'border-green-300 bg-green-900/30'
                    : 'border-green-500 bg-green-900/10 hover:border-green-400'
                }`}
                onClick={() => setActiveSession(session)}
              >
                <div className="flex justify-between items-center">
                  <span className="text-green-400 text-sm">
                    Session {session.session_id.slice(-4)}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${
                      session.ai_controlled
                        ? 'bg-purple-900/30 text-purple-400'
                        : 'bg-gray-900/30 text-gray-400'
                    }`}>
                      {session.ai_controlled ? 'AI' : 'USER'}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      session.status === 'ready'
                        ? 'bg-green-900/30 text-green-400'
                        : 'bg-yellow-900/30 text-yellow-400'
                    }`}>
                      {session.status.toUpperCase()}
                    </span>
                  </div>
                </div>
                {session.current_url && (
                  <div className="text-xs text-green-600 mt-1 truncate">
                    {session.current_url}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Session Display */}
      {activeSession && (
        <div className="mb-4 p-3 border border-green-500 rounded bg-green-900/20">
          <div className="flex justify-between items-center mb-2">
            <span className="text-green-400 font-medium">
              Session {activeSession.session_id.slice(-4)}
            </span>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded ${
                activeSession.ai_controlled
                  ? 'bg-purple-900/30 text-purple-400'
                  : 'bg-gray-900/30 text-gray-400'
              }`}>
                {activeSession.ai_controlled ? 'AI CONTROLLED' : 'USER CONTROL'}
              </span>
              <button
                onClick={() => toggleAIControl(activeSession.session_id, !activeSession.ai_controlled)}
                className={`px-2 py-1 rounded text-xs ${
                  activeSession.ai_controlled
                    ? 'bg-gray-600 text-white hover:bg-gray-500'
                    : 'bg-purple-600 text-white hover:bg-purple-500'
                }`}
              >
                {activeSession.ai_controlled ? 'TAKE CONTROL' : 'GIVE TO AI'}
              </button>
            </div>
          </div>

          {screenshot && (
            <div className="mb-2">
              <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Browser screenshot"
                className="w-full h-48 object-cover rounded border border-green-500"
              />
            </div>
          )}

          <div className="flex gap-2 mb-2">
            <input
              type="url"
              placeholder="Enter URL to navigate..."
              className="flex-1 bg-black border border-green-500 rounded px-2 py-1 text-green-400 text-sm focus:outline-none focus:border-green-400"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  navigateSession(activeSession.session_id, e.target.value);
                  e.target.value = '';
                }
              }}
            />
            <button
              onClick={() => updateScreenshot(activeSession.session_id)}
              className="px-2 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400"
            >
              REFRESH
            </button>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => executeBrowserAction(activeSession.session_id, 'click', { selector: '[type="submit"], .btn, button' })}
              className="px-2 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400"
            >
              CLICK BUTTON
            </button>
            <button
              onClick={() => executeBrowserAction(activeSession.session_id, 'scroll', { direction: 'down' })}
              className="px-2 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400"
            >
              SCROLL DOWN
            </button>
            <button
              onClick={() => executeBrowserAction(activeSession.session_id, 'extract_text', { selector: 'body' })}
              className="px-2 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400"
            >
              EXTRACT TEXT
            </button>
          </div>
        </div>
      )}

      {/* Search and Management Controls */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Search websites..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400 text-sm"
        />
        <button
          onClick={() => setShowPresetModal(true)}
          className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors text-sm"
        >
          + ADD WEBSITE
        </button>
      </div>

      {/* Website Categories */}
      <div className="flex-1 overflow-y-auto">
        {categories.map(category => (
          <WebsiteCategory
            key={category}
            category={category}
            websites={filteredWebsites.filter(w => w.category === category)}
            credentials={credentials}
            onStartSession={startBrowserSession}
            onManageCredentials={(website) => {
              setSelectedWebsite(website);
              setShowCredentialModal(true);
            }}
            onEditPreset={(website) => {
              setEditingPreset(website);
              setShowPresetModal(true);
            }}
            onDeletePreset={deletePreset}
            isLoading={isLoading}
            activeSession={activeSession}
          />
        ))}
      </div>

      {/* Ollama Instructions Panel */}
      {activeSession && (
        <OllamaInstructionsPanel
          session={activeSession}
          onExecuteAction={executeBrowserAction}
        />
      )}

      {/* Credential Management Modal */}
      {showCredentialModal && selectedWebsite && (
        <CredentialModal
          website={selectedWebsite}
          credentials={credentials[selectedWebsite.preset_id || selectedWebsite.id] || {}}
          onSave={(creds) => saveCredentials(selectedWebsite.preset_id || selectedWebsite.id, creds)}
          onClose={() => {
            setShowCredentialModal(false);
            setSelectedWebsite(null);
          }}
        />
      )}

      {/* Preset Management Modal */}
      {showPresetModal && (
        <PresetModal
          preset={editingPreset}
          onSave={async (presetData) => {
            try {
              if (editingPreset) {
                await updatePreset(editingPreset.preset_id, presetData);
              } else {
                await createPreset(presetData);
              }
              setShowPresetModal(false);
              setEditingPreset(null);
            } catch (error) {
              alert('Failed to save preset: ' + error.message);
            }
          }}
          onClose={() => {
            setShowPresetModal(false);
            setEditingPreset(null);
          }}
        />
      )}
    </div>
  );
};

// Website Category Component
const WebsiteCategory = ({ category, websites, credentials, onStartSession, onManageCredentials, onEditPreset, onDeletePreset, isLoading, activeSession }) => {
  return (
    <div className="mb-4">
      <h3 className="text-green-400 font-medium mb-2 capitalize">{category}</h3>
      <div className="space-y-2">
        {websites.map(website => (
          <WebsiteCard
            key={website.preset_id || website.id}
            website={website}
            hasCredentials={!!credentials[website.preset_id || website.id]}
            onStartSession={onStartSession}
            onManageCredentials={onManageCredentials}
            onEditPreset={onEditPreset}
            onDeletePreset={onDeletePreset}
            isLoading={isLoading}
            isActive={activeSession?.website?.preset_id === website.preset_id || activeSession?.website?.id === website.id}
          />
        ))}
      </div>
    </div>
  );
};

// Website Card Component
const WebsiteCard = ({ website, hasCredentials, onStartSession, onManageCredentials, onEditPreset, onDeletePreset, isLoading, isActive }) => {
  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${website.name}"?`)) {
      try {
        await onDeletePreset(website.preset_id || website.id);
      } catch (error) {
        console.error('Error deleting preset:', error);
        alert('Failed to delete preset');
      }
    }
  };

  const isDefault = website.preset_id && website.preset_id.startsWith('default_');

  return (
    <div className={`border rounded p-3 transition-all ${
      isActive
        ? 'border-green-300 bg-green-900/30'
        : 'border-green-500 bg-green-900/10 hover:border-green-400'
    }`}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{website.icon}</span>
          <span className="text-green-400 font-medium">{website.name}</span>
          {isDefault && <span className="text-xs text-blue-400">(Default)</span>}
        </div>
        <div className="flex items-center gap-1">
          {hasCredentials ? (
            <span className="text-xs text-green-400">🔐</span>
          ) : (
            <span className="text-xs text-yellow-400">⚠️</span>
          )}
          {!isDefault && (
            <div className="flex gap-1">
              <button
                onClick={() => onEditPreset(website)}
                className="text-xs text-blue-400 hover:text-blue-300"
                title="Edit preset"
              >
                ✏️
              </button>
              <button
                onClick={handleDelete}
                className="text-xs text-red-400 hover:text-red-300"
                title="Delete preset"
              >
                🗑️
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="text-xs text-green-600 mb-2 truncate">{website.url}</div>
      {website.description && (
        <div className="text-xs text-green-500 mb-2">{website.description}</div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onStartSession(website)}
          disabled={isLoading}
          className="flex-1 px-2 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {isLoading ? 'CONNECTING...' : 'START SESSION'}
        </button>
        <button
          onClick={() => onManageCredentials(website)}
          className="px-2 py-1 border border-green-500 text-green-400 rounded text-xs hover:bg-green-500 hover:text-black"
        >
          {hasCredentials ? 'EDIT' : 'ADD'} CREDENTIALS
        </button>
      </div>
    </div>
  );
};

// Ollama Instructions Panel
const OllamaInstructionsPanel = ({ session, onExecuteAction }) => {
  const [instructions, setInstructions] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSendInstructions = async () => {
    if (!instructions.trim() || !session) return;

    setIsSending(true);
    try {
      // Send instructions to Ollama via the chat system
      const response = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: 'browser_control',
          parameters: {
            session_id: session.session_id,
            instructions: instructions,
            action: 'ollama_instructions'
          }
        })
      });

      if (response.ok) {
        console.log('Instructions sent to Ollama successfully');
        setInstructions('');
      } else {
        console.error('Failed to send instructions to Ollama');
      }
    } catch (error) {
      console.error('Error sending instructions:', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="mt-4 p-3 border border-green-500 rounded bg-green-900/20">
      <h4 className="text-green-400 font-medium mb-2">OLLAMA INSTRUCTIONS</h4>
      <textarea
        value={instructions}
        onChange={(e) => setInstructions(e.target.value)}
        placeholder="Tell Ollama what to do with this browser session..."
        className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400 h-20 resize-none text-sm"
      />
      <div className="flex justify-end gap-2 mt-2">
        <button
          onClick={() => setInstructions('Navigate to Google and search for "AI tools"')}
          className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-500"
        >
          SEARCH EXAMPLE
        </button>
        <button
          onClick={() => setInstructions('Fill out the login form with test credentials')}
          className="px-2 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-500"
        >
          LOGIN EXAMPLE
        </button>
        <button
          onClick={handleSendInstructions}
          disabled={!instructions.trim() || isSending}
          className="px-3 py-1 bg-green-500 text-black rounded text-xs hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed"
        >
          {isSending ? 'SENDING...' : 'SEND TO OLLAMA'}
        </button>
      </div>
    </div>
  );
};

// Credential Management Modal
const CredentialModal = ({ website, credentials, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    username: credentials.username || '',
    password: '',
    remember: true
  });

  const handleSave = () => {
    if (formData.username && formData.password) {
      onSave({
        username: formData.username,
        password: formData.password,
        remember: formData.remember
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-green-500 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 className="text-lg font-bold text-green-500 mb-4">
          {website.icon} {website.name} CREDENTIALS
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-green-400 mb-1">Username/Email</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400"
              placeholder="Enter username or email..."
            />
          </div>

          <div>
            <label className="block text-sm text-green-400 mb-1">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400"
              placeholder="Enter password..."
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="remember"
              checked={formData.remember}
              onChange={(e) => setFormData({...formData, remember: e.target.checked})}
              className="h-4 w-4"
            />
            <label htmlFor="remember" className="text-sm text-green-400">
              Remember credentials
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-green-500 text-green-400 rounded hover:bg-green-500 hover:text-black transition-colors"
          >
            CANCEL
          </button>
          <button
            onClick={handleSave}
            disabled={!formData.username || !formData.password}
            className="px-4 py-2 bg-green-500 text-black rounded hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            SAVE CREDENTIALS
          </button>
        </div>
      </div>
    </div>
  );
};

// Preset Management Modal
const PresetModal = ({ preset, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    name: preset?.name || '',
    url: preset?.url || '',
    category: preset?.category || 'custom',
    icon: preset?.icon || '🌐',
    description: preset?.description || ''
  });

  const icons = ['🌐', '📧', '💼', '👥', '🐦', '💻', '📺', '🏛️', '🔍', '🎮', '📱', '💡', '🎵', '📚', '🛒', '💳', '🏦', '🏥', '🏫', '🏢'];
  const categories = ['email', 'social', 'professional', 'development', 'media', 'auction', 'search', 'entertainment', 'communication', 'finance', 'healthcare', 'education', 'shopping', 'custom'];

  const handleSave = () => {
    if (formData.name && formData.url) {
      onSave(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-green-500 rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-bold text-green-500 mb-4">
          {preset ? 'EDIT WEBSITE PRESET' : 'ADD NEW WEBSITE PRESET'}
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-green-400 mb-1">Website Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400"
              placeholder="e.g., My Bank, Company Portal..."
            />
          </div>

          <div>
            <label className="block text-sm text-green-400 mb-1">URL</label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({...formData, url: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400"
              placeholder="https://example.com"
            />
          </div>

          <div>
            <label className="block text-sm text-green-400 mb-1">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400"
            >
              {categories.map(cat => (
                <option key={cat} value={cat} className="bg-black text-green-400">
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-green-400 mb-1">Icon</label>
            <div className="grid grid-cols-10 gap-2 mb-2">
              {icons.map(icon => (
                <button
                  key={icon}
                  onClick={() => setFormData({...formData, icon})}
                  className={`p-2 border rounded text-lg hover:border-green-400 transition-colors ${
                    formData.icon === icon ? 'border-green-400 bg-green-900/30' : 'border-green-500'
                  }`}
                >
                  {icon}
                </button>
              ))}
            </div>
            <div className="text-center text-green-600 text-sm">
              Selected: {formData.icon}
            </div>
          </div>

          <div>
            <label className="block text-sm text-green-400 mb-1">Description (Optional)</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full bg-black border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:border-green-400 h-20 resize-none"
              placeholder="Brief description of this website..."
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-green-500 text-green-400 rounded hover:bg-green-500 hover:text-black transition-colors"
          >
            CANCEL
          </button>
          <button
            onClick={handleSave}
            disabled={!formData.name || !formData.url}
            className="px-4 py-2 bg-green-500 text-black rounded hover:bg-green-400 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {preset ? 'UPDATE PRESET' : 'CREATE PRESET'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default BrowserControlPanel;