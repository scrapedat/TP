import React, { useState, useRef, useCallback } from 'react';

// Tool Builder Component
const ToolBuilder = () => {
  const [canvas, setCanvas] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [connections, setConnections] = useState([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState(null);
  const canvasRef = useRef(null);

  // Available tool components
  const availableComponents = [
    {
      type: 'scraper',
      name: 'Web Scraper',
      icon: '🌐',
      color: 'cyan',
      inputs: [{ name: 'url', type: 'string' }],
      outputs: [{ name: 'data', type: 'object' }],
      config: {
        method: 'auto',
        extraction_prompt: ''
      }
    },
    {
      type: 'api',
      name: 'API Connector',
      icon: '🔗',
      color: 'blue',
      inputs: [{ name: 'endpoint', type: 'string' }, { name: 'params', type: 'object' }],
      outputs: [{ name: 'response', type: 'object' }],
      config: {
        method: 'GET',
        headers: {}
      }
    },
    {
      type: 'processor',
      name: 'Data Processor',
      icon: '⚙️',
      color: 'yellow',
      inputs: [{ name: 'input', type: 'any' }],
      outputs: [{ name: 'output', type: 'any' }],
      config: {
        operation: 'transform',
        rules: []
      }
    },
    {
      type: 'storage',
      name: 'Data Storage',
      icon: '💾',
      color: 'green',
      inputs: [{ name: 'data', type: 'any' }],
      outputs: [],
      config: {
        list_name: '',
        list_type: 'general'
      }
    },
    {
      type: 'filter',
      name: 'Data Filter',
      icon: '🔍',
      color: 'purple',
      inputs: [{ name: 'data', type: 'array' }, { name: 'criteria', type: 'object' }],
      outputs: [{ name: 'filtered', type: 'array' }],
      config: {
        filter_type: 'contains',
        field: '',
        value: ''
      }
    },
    {
      type: 'email',
      name: 'Email Sender',
      icon: '📧',
      color: 'red',
      inputs: [{ name: 'to', type: 'string' }, { name: 'subject', type: 'string' }, { name: 'body', type: 'string' }],
      outputs: [{ name: 'sent', type: 'boolean' }],
      config: {
        account: 'default'
      }
    }
  ];

  const addComponentToCanvas = useCallback((component, x, y) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type: component.type,
      name: component.name,
      icon: component.icon,
      color: component.color,
      position: { x, y },
      inputs: component.inputs,
      outputs: component.outputs,
      config: { ...component.config },
      data: {}
    };

    setCanvas(prev => [...prev, newNode]);
  }, []);

  const handleCanvasClick = useCallback((e) => {
    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // If clicking on empty canvas, deselect
    if (e.target === canvasRef.current) {
      setSelectedNode(null);
    }
  }, []);

  const handleNodeClick = useCallback((node, e) => {
    e.stopPropagation();
    setSelectedNode(node);
  }, []);

  const handleNodeDrag = useCallback((nodeId, newPosition) => {
    setCanvas(prev => prev.map(node =>
      node.id === nodeId
        ? { ...node, position: newPosition }
        : node
    ));
  }, []);

  const deleteNode = useCallback((nodeId) => {
    setCanvas(prev => prev.filter(node => node.id !== nodeId));
    setConnections(prev => prev.filter(conn =>
      conn.from.nodeId !== nodeId && conn.to.nodeId !== nodeId
    ));
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null);
    }
  }, []);

  const startConnection = useCallback((nodeId, portType, portName, isOutput) => {
    setIsConnecting(true);
    setConnectionStart({ nodeId, portType, portName, isOutput });
  }, []);

  const completeConnection = useCallback((nodeId, portType, portName, isOutput) => {
    if (!isConnecting || !connectionStart) return;

    // Validate connection
    const fromOutput = connectionStart.isOutput;
    const toInput = !isOutput;

    if (fromOutput && toInput && connectionStart.nodeId !== nodeId) {
      const newConnection = {
        id: `conn_${Date.now()}`,
        from: {
          nodeId: connectionStart.nodeId,
          portType: connectionStart.portType,
          portName: connectionStart.portName
        },
        to: {
          nodeId: nodeId,
          portType: portType,
          portName: portName
        }
      };

      setConnections(prev => [...prev, newConnection]);
    }

    setIsConnecting(false);
    setConnectionStart(null);
  }, [isConnecting, connectionStart]);

  const deleteConnection = useCallback((connectionId) => {
    setConnections(prev => prev.filter(conn => conn.id !== connectionId));
  }, []);

  const updateNodeConfig = useCallback((nodeId, config) => {
    setCanvas(prev => prev.map(node =>
      node.id === nodeId
        ? { ...node, config: { ...node.config, ...config } }
        : node
    ));
  }, []);

  const exportWorkflow = useCallback(() => {
    const workflow = {
      nodes: canvas,
      connections: connections,
      metadata: {
        name: 'Custom Workflow',
        description: 'Generated workflow from Tool Builder',
        created: new Date().toISOString()
      }
    };

    const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [canvas, connections]);

  const runWorkflow = useCallback(async () => {
    // Placeholder for workflow execution
    console.log('Running workflow:', { canvas, connections });
    // This would integrate with the backend to execute the workflow
  }, [canvas, connections]);

  return (
    <div className="tool-builder bg-black/80 border-2 border-yellow-500 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-yellow-500">TOOL BUILDER</h2>
        <div className="flex gap-2">
          <button
            onClick={exportWorkflow}
            className="px-3 py-1 bg-yellow-500 text-black rounded hover:bg-yellow-400 transition-colors"
          >
            EXPORT
          </button>
          <button
            onClick={runWorkflow}
            className="px-3 py-1 bg-green-500 text-black rounded hover:bg-green-400 transition-colors"
          >
            RUN
          </button>
        </div>
      </div>

      <div className="flex flex-1 gap-4">
        {/* Component Palette */}
        <div className="w-64 bg-black/50 border border-yellow-500 rounded p-3">
          <h3 className="text-yellow-400 font-medium mb-3">COMPONENTS</h3>
          <div className="space-y-2">
            {availableComponents.map(component => (
              <DraggableComponent
                key={component.type}
                component={component}
                onAddToCanvas={addComponentToCanvas}
              />
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 bg-black/30 border border-yellow-500 rounded relative overflow-hidden">
          <canvas
            ref={canvasRef}
            className="w-full h-full cursor-crosshair"
            onClick={handleCanvasClick}
          />

          {/* Render connections */}
          <svg className="absolute inset-0 pointer-events-none">
            {connections.map(connection => (
              <ConnectionLine
                key={connection.id}
                connection={connection}
                nodes={canvas}
                onDelete={() => deleteConnection(connection.id)}
              />
            ))}
          </svg>

          {/* Render nodes */}
          {canvas.map(node => (
            <CanvasNode
              key={node.id}
              node={node}
              isSelected={selectedNode?.id === node.id}
              onClick={(e) => handleNodeClick(node, e)}
              onDrag={handleNodeDrag}
              onDelete={() => deleteNode(node.id)}
              onPortClick={startConnection}
              isConnecting={isConnecting}
            />
          ))}

          {/* Connection preview */}
          {isConnecting && connectionStart && (
            <ConnectionPreview
              startNode={canvas.find(n => n.id === connectionStart.nodeId)}
              startPort={connectionStart}
            />
          )}
        </div>

        {/* Properties Panel */}
        <div className="w-64 bg-black/50 border border-yellow-500 rounded p-3">
          {selectedNode ? (
            <NodeProperties
              node={selectedNode}
              onUpdateConfig={updateNodeConfig}
            />
          ) : (
            <div className="text-yellow-600 text-center py-8">
              Select a node to edit properties
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Draggable Component for Palette
const DraggableComponent = ({ component, onAddToCanvas }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragStart = useCallback((e) => {
    setIsDragging(true);
    e.dataTransfer.setData('component', JSON.stringify(component));
  }, [component]);

  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      className={`p-2 border border-yellow-500 rounded cursor-move transition-all ${
        isDragging ? 'opacity-50' : 'hover:border-yellow-400'
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-lg">{component.icon}</span>
        <span className="text-yellow-400 text-sm">{component.name}</span>
      </div>
    </div>
  );
};

// Canvas Node Component
const CanvasNode = ({ node, isSelected, onClick, onDrag, onDelete, onPortClick, isConnecting }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const nodeRef = useRef(null);

  const handleMouseDown = useCallback((e) => {
    if (e.target.closest('.port')) return; // Don't drag if clicking on port

    setIsDragging(true);
    const rect = nodeRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;

    const canvas = nodeRef.current.closest('.tool-builder');
    const canvasRect = canvas.getBoundingClientRect();

    const newX = e.clientX - canvasRect.left - dragOffset.x;
    const newY = e.clientY - canvasRect.top - dragOffset.y;

    onDrag(node.id, { x: Math.max(0, newX), y: Math.max(0, newY) });
  }, [isDragging, dragOffset, node.id, onDrag]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const colorClasses = {
    cyan: 'border-cyan-400 bg-cyan-900/20',
    blue: 'border-blue-400 bg-blue-900/20',
    yellow: 'border-yellow-400 bg-yellow-900/20',
    green: 'border-green-400 bg-green-900/20',
    purple: 'border-purple-400 bg-purple-900/20',
    red: 'border-red-400 bg-red-900/20'
  };

  return (
    <div
      ref={nodeRef}
      className={`absolute border-2 rounded p-2 cursor-move min-w-32 ${
        isSelected ? 'ring-2 ring-yellow-400' : ''
      } ${colorClasses[node.color]}`}
      style={{
        left: node.position.x,
        top: node.position.y,
        zIndex: isSelected ? 10 : 1
      }}
      onClick={onClick}
      onMouseDown={handleMouseDown}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1">
          <span>{node.icon}</span>
          <span className="text-xs font-medium truncate max-w-20">{node.name}</span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="text-red-400 hover:text-red-300 text-xs"
        >
          ×
        </button>
      </div>

      {/* Input Ports */}
      {node.inputs.length > 0 && (
        <div className="mb-1">
          {node.inputs.map(input => (
            <div key={input.name} className="flex items-center gap-1 mb-1">
              <div
                className="port w-2 h-2 bg-gray-400 rounded-full cursor-pointer hover:bg-gray-300"
                onClick={(e) => {
                  e.stopPropagation();
                  onPortClick(node.id, input.type, input.name, false);
                }}
              />
              <span className="text-xs text-gray-300">{input.name}</span>
            </div>
          ))}
        </div>
      )}

      {/* Output Ports */}
      {node.outputs.length > 0 && (
        <div>
          {node.outputs.map(output => (
            <div key={output.name} className="flex items-center justify-end gap-1 mb-1">
              <span className="text-xs text-gray-300">{output.name}</span>
              <div
                className="port w-2 h-2 bg-gray-400 rounded-full cursor-pointer hover:bg-gray-300"
                onClick={(e) => {
                  e.stopPropagation();
                  onPortClick(node.id, output.type, output.name, true);
                }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Connection Line Component
const ConnectionLine = ({ connection, nodes, onDelete }) => {
  const fromNode = nodes.find(n => n.id === connection.from.nodeId);
  const toNode = nodes.find(n => n.id === connection.to.nodeId);

  if (!fromNode || !toNode) return null;

  const fromX = fromNode.position.x + 120; // Approximate output port position
  const fromY = fromNode.position.y + 30;
  const toX = toNode.position.x;
  const toY = toNode.position.y + 30;

  return (
    <g>
      <line
        x1={fromX}
        y1={fromY}
        x2={toX}
        y2={toY}
        stroke="#fbbf24"
        strokeWidth="2"
        className="cursor-pointer hover:stroke-red-400"
        onClick={onDelete}
      />
      {/* Arrow head */}
      <polygon
        points={`${toX-5},${toY-3} ${toX-5},${toY+3} ${toX},${toY}`}
        fill="#fbbf24"
      />
    </g>
  );
};

// Node Properties Panel
const NodeProperties = ({ node, onUpdateConfig }) => {
  const [config, setConfig] = useState(node.config);

  const handleConfigChange = (key, value) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    onUpdateConfig(node.id, newConfig);
  };

  return (
    <div>
      <h3 className="text-yellow-400 font-medium mb-3">{node.icon} {node.name}</h3>

      <div className="space-y-3">
        {Object.entries(config).map(([key, value]) => (
          <div key={key}>
            <label className="block text-xs text-yellow-400 mb-1 capitalize">
              {key.replace('_', ' ')}
            </label>
            {typeof value === 'string' && (
              <input
                type="text"
                value={value}
                onChange={(e) => handleConfigChange(key, e.target.value)}
                className="w-full bg-black border border-yellow-500 rounded px-2 py-1 text-yellow-400 text-xs focus:outline-none focus:border-yellow-400"
              />
            )}
            {typeof value === 'boolean' && (
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => handleConfigChange(key, e.target.checked)}
                className="h-4 w-4"
              />
            )}
            {typeof value === 'object' && (
              <textarea
                value={JSON.stringify(value, null, 2)}
                onChange={(e) => {
                  try {
                    handleConfigChange(key, JSON.parse(e.target.value));
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                className="w-full bg-black border border-yellow-500 rounded px-2 py-1 text-yellow-400 text-xs focus:outline-none focus:border-yellow-400 h-20"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Connection Preview Component
const ConnectionPreview = ({ startNode, startPort }) => {
  // This would show a preview line while connecting
  return null; // Placeholder
};

export default ToolBuilder;