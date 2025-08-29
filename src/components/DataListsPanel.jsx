import React, { useState, useEffect } from 'react';

// Data Lists Management Panel
const DataListsPanel = () => {
  const [lists, setLists] = useState([]);
  const [activeList, setActiveList] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  // Load data lists on component mount
  useEffect(() => {
    loadLists();
  }, []);

  const loadLists = async () => {
    try {
      const response = await fetch('/api/data/lists');
      if (response.ok) {
        const data = await response.json();
        setLists(data.lists || []);
      }
    } catch (error) {
      console.error('Error loading lists:', error);
    }
  };

  const createList = async (listData) => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/data/lists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(listData)
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await loadLists();
          setShowCreateModal(false);
        }
      }
    } catch (error) {
      console.error('Error creating list:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addItemToList = async (listId, itemData) => {
    try {
      const response = await fetch('/api/data/lists/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          list_id: listId,
          data: itemData,
          source: 'dashboard'
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          await loadLists(); // Refresh to show updated count
        }
      }
    } catch (error) {
      console.error('Error adding item:', error);
    }
  };

  const exportList = async (listId, format) => {
    try {
      const response = await fetch(`/api/data/lists/${listId}/export?format=${format}`);
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Create download link
          const blob = new Blob([result.data], { type: 'text/plain' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `list_${listId}.${format}`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }
      }
    } catch (error) {
      console.error('Error exporting list:', error);
    }
  };

  const searchLists = async (query) => {
    if (!query.trim()) {
      await loadLists();
      return;
    }

    try {
      const response = await fetch(`/api/data/search?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setLists(data.results?.map(r => r.list) || []);
      }
    } catch (error) {
      console.error('Error searching lists:', error);
    }
  };

  const filteredLists = lists.filter(list => {
    if (filterType !== 'all' && list.type !== filterType) return false;
    return true;
  });

  return (
    <div className="data-lists-panel bg-black/80 border-2 border-cyan-400 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-cyan-400">DATA LISTS</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-3 py-1 bg-cyan-400 text-black rounded hover:bg-cyan-300 transition-colors"
        >
          + NEW LIST
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Search lists..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            searchLists(e.target.value);
          }}
          className="flex-1 bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 placeholder-cyan-600 focus:outline-none focus:border-cyan-300"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 focus:outline-none focus:border-cyan-300"
        >
          <option value="all">All Types</option>
          <option value="urls">URLs</option>
          <option value="emails">Emails</option>
          <option value="phones">Phones</option>
          <option value="research">Research</option>
          <option value="general">General</option>
        </select>
      </div>

      {/* Lists Grid */}
      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredLists.map(list => (
            <ListCard
              key={list.id}
              list={list}
              onSelect={() => setActiveList(list)}
              onExport={(format) => exportList(list.id, format)}
              isActive={activeList?.id === list.id}
            />
          ))}
        </div>

        {filteredLists.length === 0 && (
          <div className="text-center text-cyan-600 py-8">
            {searchQuery ? 'No lists found matching your search.' : 'No data lists yet. Create your first list!'}
          </div>
        )}
      </div>

      {/* Create List Modal */}
      {showCreateModal && (
        <CreateListModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createList}
          isLoading={isLoading}
        />
      )}

      {/* List Details Panel */}
      {activeList && (
        <ListDetailsPanel
          list={activeList}
          onClose={() => setActiveList(null)}
          onAddItem={(itemData) => addItemToList(activeList.id, itemData)}
        />
      )}
    </div>
  );
};

// List Card Component
const ListCard = ({ list, onSelect, onExport, isActive }) => {
  const getTypeColor = (type) => {
    const colors = {
      urls: 'text-blue-400',
      emails: 'text-green-400',
      phones: 'text-yellow-400',
      research: 'text-purple-400',
      general: 'text-cyan-400'
    };
    return colors[type] || 'text-cyan-400';
  };

  return (
    <div
      className={`border-2 rounded-lg p-3 cursor-pointer transition-all hover:border-cyan-300 ${
        isActive ? 'border-cyan-300 bg-cyan-900/20' : 'border-cyan-400 bg-cyan-900/10'
      }`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-cyan-400 truncate">{list.name}</h3>
        <span className={`text-xs px-2 py-1 rounded ${getTypeColor(list.type)} bg-black/50`}>
          {list.type}
        </span>
      </div>

      {list.description && (
        <p className="text-xs text-cyan-600 mb-2 line-clamp-2">{list.description}</p>
      )}

      <div className="flex justify-between items-center text-xs text-cyan-500">
        <span>{list.items?.length || 0} items</span>
        <div className="flex gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExport('json');
            }}
            className="px-2 py-1 bg-cyan-400 text-black rounded text-xs hover:bg-cyan-300"
          >
            JSON
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExport('csv');
            }}
            className="px-2 py-1 bg-cyan-400 text-black rounded text-xs hover:bg-cyan-300"
          >
            CSV
          </button>
        </div>
      </div>
    </div>
  );
};

// Create List Modal
const CreateListModal = ({ onClose, onCreate, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    list_type: 'general'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.name.trim()) {
      onCreate(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-cyan-400 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 className="text-lg font-bold text-cyan-400 mb-4">CREATE NEW LIST</h3>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-cyan-400 mb-1">List Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full bg-black border border-cyan-400 rounded px-3 py-2 text-cyan-400 focus:outline-none focus:border-cyan-300"
                placeholder="Enter list name..."
                required
              />
            </div>

            <div>
              <label className="block text-sm text-cyan-400 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full bg-black border border-cyan-400 rounded px-3 py-2 text-cyan-400 focus:outline-none focus:border-cyan-300 h-20 resize-none"
                placeholder="Optional description..."
              />
            </div>

            <div>
              <label className="block text-sm text-cyan-400 mb-1">List Type</label>
              <select
                value={formData.list_type}
                onChange={(e) => setFormData({...formData, list_type: e.target.value})}
                className="w-full bg-black border border-cyan-400 rounded px-3 py-2 text-cyan-400 focus:outline-none focus:border-cyan-300"
              >
                <option value="general">General</option>
                <option value="urls">URLs</option>
                <option value="emails">Emails</option>
                <option value="phones">Phones</option>
                <option value="research">Research</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-400 hover:text-black transition-colors"
            >
              CANCEL
            </button>
            <button
              type="submit"
              disabled={isLoading || !formData.name.trim()}
              className="px-4 py-2 bg-cyan-400 text-black rounded hover:bg-cyan-300 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'CREATING...' : 'CREATE'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// List Details Panel
const ListDetailsPanel = ({ list, onClose, onAddItem }) => {
  const [newItem, setNewItem] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddItem = () => {
    if (Object.keys(newItem).length > 0) {
      onAddItem(newItem);
      setNewItem({});
      setShowAddForm(false);
    }
  };

  const renderItemData = (data) => {
    if (typeof data === 'object') {
      return (
        <div className="space-y-1">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-cyan-400">{key}:</span>
              <span className="text-cyan-300 ml-2">{String(value)}</span>
            </div>
          ))}
        </div>
      );
    }
    return <span className="text-cyan-300">{String(data)}</span>;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-cyan-400 rounded-lg w-full max-w-4xl mx-4 h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-cyan-400">
          <div>
            <h3 className="text-xl font-bold text-cyan-400">{list.name}</h3>
            <p className="text-sm text-cyan-600">{list.description}</p>
          </div>
          <button
            onClick={onClose}
            className="text-cyan-400 hover:text-cyan-300 text-xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Add Item Button */}
          <div className="mb-4">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-3 py-1 bg-cyan-400 text-black rounded hover:bg-cyan-300 transition-colors"
            >
              + ADD ITEM
            </button>
          </div>

          {/* Add Item Form */}
          {showAddForm && (
            <div className="mb-4 p-3 border border-cyan-400 rounded">
              <h4 className="text-cyan-400 mb-2">Add New Item</h4>
              <div className="space-y-2">
                {list.type === 'urls' && (
                  <input
                    type="url"
                    placeholder="Enter URL..."
                    onChange={(e) => setNewItem({ url: e.target.value, title: '', description: '' })}
                    className="w-full bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 focus:outline-none focus:border-cyan-300"
                  />
                )}
                {list.type === 'emails' && (
                  <input
                    type="email"
                    placeholder="Enter email..."
                    onChange={(e) => setNewItem({ email: e.target.value, name: '', company: '' })}
                    className="w-full bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 focus:outline-none focus:border-cyan-300"
                  />
                )}
                {list.type === 'phones' && (
                  <input
                    type="tel"
                    placeholder="Enter phone number..."
                    onChange={(e) => setNewItem({ phone: e.target.value, name: '', type: 'mobile' })}
                    className="w-full bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 focus:outline-none focus:border-cyan-300"
                  />
                )}
                {(list.type === 'research' || list.type === 'general') && (
                  <div className="space-y-2">
                    <input
                      type="text"
                      placeholder="Title..."
                      onChange={(e) => setNewItem({...newItem, title: e.target.value})}
                      className="w-full bg-black border border-cyan-400 rounded px-3 py-1 text-cyan-400 focus:outline-none focus:border-cyan-300"
                    />
                    <textarea
                      placeholder="Content..."
                      onChange={(e) => setNewItem({...newItem, content: e.target.value})}
                      className="w-full bg-black border border-cyan-400 rounded px-3 py-2 text-cyan-400 focus:outline-none focus:border-cyan-300 h-20 resize-none"
                    />
                  </div>
                )}
                <div className="flex gap-2">
                  <button
                    onClick={handleAddItem}
                    className="px-3 py-1 bg-cyan-400 text-black rounded hover:bg-cyan-300"
                  >
                    ADD
                  </button>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="px-3 py-1 border border-cyan-400 text-cyan-400 rounded hover:bg-cyan-300"
                  >
                    CANCEL
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Items List */}
          <div className="space-y-2">
            {list.items?.map((item, index) => (
              <div key={item.id || index} className="border border-cyan-400 rounded p-3">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs text-cyan-600">
                    {new Date(item.added_at).toLocaleString()}
                  </span>
                  {item.source && (
                    <span className="text-xs text-cyan-500 bg-cyan-900/30 px-2 py-1 rounded">
                      {item.source}
                    </span>
                  )}
                </div>
                {renderItemData(item.data)}
              </div>
            )) || (
              <div className="text-center text-cyan-600 py-8">
                No items in this list yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataListsPanel;