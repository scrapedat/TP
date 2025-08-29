import React, { useState, useEffect } from 'react';

// Model Manager Component
const ModelManager = () => {
  const [models, setModels] = useState({});
  const [activeModels, setActiveModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('llama3');
  const [taskType, setTaskType] = useState('general_chat');
  const [isLoading, setIsLoading] = useState(false);
  const [modelStatus, setModelStatus] = useState(null);
  const [performanceStats, setPerformanceStats] = useState({});

  // Available task types
  const taskTypes = {
    general_chat: { name: 'General Chat', icon: '💬', description: 'General conversation and Q&A' },
    web_search: { name: 'Web Search', icon: '🔍', description: 'Web search and information retrieval' },
    code_generation: { name: 'Code Generation', icon: '💻', description: 'Code writing and programming tasks' },
    image_analysis: { name: 'Image Analysis', icon: '🖼️', description: 'Image understanding and analysis' },
    complex_analysis: { name: 'Complex Analysis', icon: '🧠', description: 'Complex reasoning and analysis tasks' },
    creative_writing: { name: 'Creative Writing', icon: '✍️', description: 'Creative writing and content generation' },
    fast_response: { name: 'Fast Response', icon: '⚡', description: 'Quick responses and simple tasks' }
  };

  // Load model status on component mount
  useEffect(() => {
    loadModelStatus();
    const interval = setInterval(loadModelStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadModelStatus = async () => {
    try {
      const response = await fetch('/api/models/status');
      if (response.ok) {
        const data = await response.json();
        setModels(data.models || {});
        setActiveModels(data.active_model_names || []);
        setPerformanceStats(data.performance_stats || {});
        setModelStatus(data);
      }
    } catch (error) {
      console.error('Error loading model status:', error);
    }
  };

  const refreshModels = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/models/refresh', { method: 'POST' });
      if (response.ok) {
        await loadModelStatus();
      }
    } catch (error) {
      console.error('Error refreshing models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadModel = async (modelName) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/models/load/${modelName}`, { method: 'POST' });
      if (response.ok) {
        await loadModelStatus();
      }
    } catch (error) {
      console.error('Error loading model:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectOptimalModel = async () => {
    try {
      const response = await fetch('/api/models/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_type: taskType })
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedModel(data.selected_model);
      }
    } catch (error) {
      console.error('Error selecting model:', error);
    }
  };

  const testModel = async (modelName) => {
    try {
      const response = await fetch('/api/models/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: modelName,
          prompt: "Hello! Can you tell me about yourself in one sentence?",
          task_type: "general_chat"
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert(`✅ ${modelName}: ${data.response}`);
        } else {
          alert(`❌ ${modelName}: ${data.error}`);
        }
      }
    } catch (error) {
      console.error('Error testing model:', error);
      alert(`❌ Error testing ${modelName}`);
    }
  };

  const getModelIcon = (modelName) => {
    if (modelName.includes('llama')) return '🦙';
    if (modelName.includes('phi')) return '🌀';
    if (modelName.includes('mistral')) return '🌪️';
    if (modelName.includes('code')) return '💻';
    if (modelName.includes('vision') || modelName.includes('llava')) return '👁️';
    return '🤖';
  };

  const getCapabilityColor = (capability) => {
    const colors = {
      text_generation: 'bg-blue-500',
      conversation: 'bg-green-500',
      analysis: 'bg-purple-500',
      coding: 'bg-orange-500',
      vision: 'bg-red-500',
      web_search: 'bg-cyan-500',
      complex_reasoning: 'bg-yellow-500',
      fast_inference: 'bg-gray-500',
      creative_writing: 'bg-pink-500'
    };
    return colors[capability] || 'bg-gray-500';
  };

  return (
    <div className="model-manager bg-black/80 border-2 border-purple-500 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-purple-500">MODEL MANAGER</h2>
        <div className="flex gap-2">
          <button
            onClick={refreshModels}
            disabled={isLoading}
            className="px-3 py-1 bg-purple-500 text-black rounded hover:bg-purple-400 disabled:bg-gray-600 disabled:cursor-not-allowed"
          >
            {isLoading ? 'REFRESHING...' : '🔄 REFRESH'}
          </button>
        </div>
      </div>

      <div className="flex flex-1 gap-4">
        {/* Model List */}
        <div className="w-1/2 bg-black/50 border border-purple-500 rounded p-3">
          <h3 className="text-purple-400 font-medium mb-3">AVAILABLE MODELS</h3>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {Object.entries(models).map(([name, info]) => (
              <div
                key={name}
                className={`p-2 border rounded transition-all ${
                  activeModels.includes(name)
                    ? 'border-green-400 bg-green-900/20'
                    : 'border-purple-500 bg-purple-900/10 hover:border-purple-400'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{getModelIcon(name)}</span>
                    <span className="text-purple-400 font-medium text-sm">{name}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {activeModels.includes(name) ? (
                      <span className="text-xs text-green-400">ACTIVE</span>
                    ) : (
                      <button
                        onClick={() => loadModel(name)}
                        disabled={isLoading}
                        className="px-2 py-1 bg-purple-500 text-black rounded text-xs hover:bg-purple-400 disabled:bg-gray-600"
                      >
                        LOAD
                      </button>
                    )}
                    <button
                      onClick={() => testModel(name)}
                      className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-400"
                    >
                      TEST
                    </button>
                  </div>
                </div>

                <div className="text-xs text-purple-600 mb-2">
                  Size: {info.size} • Modified: {new Date(info.modified_at).toLocaleDateString()}
                </div>

                {/* Performance Stats */}
                {performanceStats[name] && (
                  <div className="text-xs text-purple-500">
                    Perf: {performanceStats[name].performance_score?.toFixed(2) || 'N/A'} •
                    Speed: {performanceStats[name].tokens_per_second?.toFixed(1) || 'N/A'} tok/s
                  </div>
                )}
              </div>
            ))}
          </div>

          {Object.keys(models).length === 0 && (
            <div className="text-center text-purple-600 py-8">
              No models found. Make sure Ollama is running and models are installed.
            </div>
          )}
        </div>

        {/* Model Selection & Tasks */}
        <div className="w-1/2 bg-black/50 border border-purple-500 rounded p-3">
          <h3 className="text-purple-400 font-medium mb-3">MODEL SELECTION</h3>

          {/* Current Selection */}
          <div className="mb-4 p-3 border border-purple-500 rounded bg-purple-900/20">
            <div className="text-sm text-purple-400 mb-1">Selected Model:</div>
            <div className="text-lg text-purple-300 font-medium">
              {getModelIcon(selectedModel)} {selectedModel}
            </div>
          </div>

          {/* Task Type Selection */}
          <div className="mb-4">
            <label className="block text-sm text-purple-400 mb-2">Task Type:</label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-black border border-purple-500 rounded px-3 py-2 text-purple-400 focus:outline-none focus:border-purple-400"
            >
              {Object.entries(taskTypes).map(([key, task]) => (
                <option key={key} value={key}>
                  {task.icon} {task.name}
                </option>
              ))}
            </select>
            <div className="text-xs text-purple-600 mt-1">
              {taskTypes[taskType]?.description}
            </div>
          </div>

          {/* Auto-Select Button */}
          <button
            onClick={selectOptimalModel}
            className="w-full mb-4 px-3 py-2 bg-purple-500 text-black rounded hover:bg-purple-400 transition-colors"
          >
            🎯 SELECT OPTIMAL MODEL
          </button>

          {/* Task Capabilities */}
          <div className="mb-4">
            <h4 className="text-purple-400 font-medium mb-2">Required Capabilities:</h4>
            <div className="flex flex-wrap gap-1">
              {/* This would be populated based on the selected task type */}
              <span className="px-2 py-1 bg-blue-500 text-white rounded text-xs">text_generation</span>
              <span className="px-2 py-1 bg-green-500 text-white rounded text-xs">conversation</span>
            </div>
          </div>

          {/* Model Capabilities */}
          <div>
            <h4 className="text-purple-400 font-medium mb-2">Model Capabilities:</h4>
            <div className="max-h-32 overflow-y-auto">
              {activeModels.includes(selectedModel) && (
                <div className="space-y-1">
                  {/* This would show actual capabilities for the selected model */}
                  <div className="flex flex-wrap gap-1">
                    <span className="px-2 py-1 bg-blue-500 text-white rounded text-xs">text_generation</span>
                    <span className="px-2 py-1 bg-green-500 text-white rounded text-xs">conversation</span>
                    <span className="px-2 py-1 bg-purple-500 text-white rounded text-xs">analysis</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* System Stats */}
          {modelStatus && (
            <div className="mt-4 pt-3 border-t border-purple-500">
              <h4 className="text-purple-400 font-medium mb-2">System Stats:</h4>
              <div className="text-xs text-purple-600 space-y-1">
                <div>Total Models: {modelStatus.total_models}</div>
                <div>Active Models: {modelStatus.active_models}</div>
                <div>Tasks Available: {Object.keys(taskTypes).length}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ModelManager;