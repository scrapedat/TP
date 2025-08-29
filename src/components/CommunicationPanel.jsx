import React, { useState, useEffect } from 'react';

// Communication Hub Panel
const CommunicationPanel = () => {
  const [emailAccounts, setEmailAccounts] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [scheduledEmails, setScheduledEmails] = useState([]);
  const [showEmailComposer, setShowEmailComposer] = useState(false);
  const [activeTab, setActiveTab] = useState('emails');

  // Load data on component mount
  useEffect(() => {
    loadEmailAccounts();
    loadTemplates();
    loadScheduledEmails();
  }, []);

  const loadEmailAccounts = async () => {
    // Placeholder for email account loading
    setEmailAccounts([
      { id: '1', email: 'user@gmail.com', provider: 'gmail', connected: true },
      { id: '2', email: 'work@company.com', provider: 'outlook', connected: false }
    ]);
  };

  const loadTemplates = async () => {
    // Placeholder for email templates
    setTemplates([
      {
        id: '1',
        name: 'Research Follow-up',
        subject: 'Following up on our research discussion',
        body: 'Dear {{name}},\n\nI wanted to follow up on our recent discussion about {{topic}}. I\'ve attached some additional research materials for your review.\n\nBest regards,\n{{sender}}'
      },
      {
        id: '2',
        name: 'Data Collection Request',
        subject: 'Request for data collection assistance',
        body: 'Hello {{name}},\n\nI\'m working on collecting data related to {{topic}} and would appreciate your assistance with the following:\n\n{{request_details}}\n\nThank you for your help.\n\nBest,\n{{sender}}'
      }
    ]);
  };

  const loadScheduledEmails = async () => {
    // Placeholder for scheduled emails
    setScheduledEmails([
      {
        id: '1',
        to: 'researcher@university.edu',
        subject: 'Research collaboration opportunity',
        scheduled_for: '2024-01-15T10:00:00Z',
        status: 'pending'
      }
    ]);
  };

  const sendEmail = async (emailData) => {
    try {
      const response = await fetch('/api/communication/send_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData)
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          console.log('Email sent successfully');
          setShowEmailComposer(false);
        }
      }
    } catch (error) {
      console.error('Error sending email:', error);
    }
  };

  const connectEmailAccount = async (provider) => {
    // Placeholder for OAuth flow
    if (provider === 'gmail') {
      window.open('/auth/gmail', '_blank');
    }
  };

  return (
    <div className="communication-panel bg-black/80 border-2 border-fuchsia-500 rounded-lg p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-fuchsia-500">COMMUNICATION HUB</h2>
        <button
          onClick={() => setShowEmailComposer(true)}
          className="px-3 py-1 bg-fuchsia-500 text-black rounded hover:bg-fuchsia-400 transition-colors"
        >
          ✉️ COMPOSE
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4">
        {[
          { id: 'emails', label: 'EMAILS', icon: '✉️' },
          { id: 'templates', label: 'TEMPLATES', icon: '📝' },
          { id: 'scheduled', label: 'SCHEDULED', icon: '⏰' },
          { id: 'accounts', label: 'ACCOUNTS', icon: '🔑' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              activeTab === tab.id
                ? 'bg-fuchsia-500 text-black'
                : 'bg-fuchsia-900/30 text-fuchsia-400 hover:bg-fuchsia-900/50'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'emails' && (
          <EmailHistory emails={[]} />
        )}

        {activeTab === 'templates' && (
          <EmailTemplates
            templates={templates}
            onUseTemplate={(template) => {
              setShowEmailComposer(true);
              // Pre-fill composer with template
            }}
          />
        )}

        {activeTab === 'scheduled' && (
          <ScheduledEmails
            emails={scheduledEmails}
            onCancel={(id) => {
              setScheduledEmails(prev => prev.filter(email => email.id !== id));
            }}
          />
        )}

        {activeTab === 'accounts' && (
          <EmailAccounts
            accounts={emailAccounts}
            onConnect={connectEmailAccount}
          />
        )}
      </div>

      {/* Email Composer Modal */}
      {showEmailComposer && (
        <EmailComposer
          onClose={() => setShowEmailComposer(false)}
          onSend={sendEmail}
          templates={templates}
        />
      )}
    </div>
  );
};

// Email History Component
const EmailHistory = ({ emails }) => {
  return (
    <div className="space-y-2">
      {emails.length === 0 ? (
        <div className="text-center text-fuchsia-600 py-8">
          No emails sent yet. Compose your first email!
        </div>
      ) : (
        emails.map(email => (
          <div key={email.id} className="border border-fuchsia-500 rounded p-3">
            <div className="flex justify-between items-start mb-1">
              <span className="text-fuchsia-400 font-medium">To: {email.to}</span>
              <span className="text-xs text-fuchsia-600">
                {new Date(email.sent_at).toLocaleString()}
              </span>
            </div>
            <div className="text-sm text-fuchsia-300 mb-1">{email.subject}</div>
            <div className="text-xs text-fuchsia-500">
              Status: {email.status} • {email.provider}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

// Email Templates Component
const EmailTemplates = ({ templates, onUseTemplate }) => {
  return (
    <div className="space-y-3">
      {templates.map(template => (
        <div key={template.id} className="border border-fuchsia-500 rounded p-3">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-fuchsia-400 font-medium">{template.name}</h3>
            <button
              onClick={() => onUseTemplate(template)}
              className="px-2 py-1 bg-fuchsia-500 text-black rounded text-xs hover:bg-fuchsia-400"
            >
              USE
            </button>
          </div>
          <div className="text-sm text-fuchsia-300 mb-1">{template.subject}</div>
          <div className="text-xs text-fuchsia-600 line-clamp-3">
            {template.body.substring(0, 100)}...
          </div>
        </div>
      ))}
    </div>
  );
};

// Scheduled Emails Component
const ScheduledEmails = ({ emails, onCancel }) => {
  return (
    <div className="space-y-2">
      {emails.map(email => (
        <div key={email.id} className="border border-fuchsia-500 rounded p-3">
          <div className="flex justify-between items-start mb-1">
            <span className="text-fuchsia-400">To: {email.to}</span>
            <button
              onClick={() => onCancel(email.id)}
              className="text-red-400 hover:text-red-300 text-sm"
            >
              ✕
            </button>
          </div>
          <div className="text-sm text-fuchsia-300 mb-1">{email.subject}</div>
          <div className="text-xs text-fuchsia-500">
            Scheduled: {new Date(email.scheduled_for).toLocaleString()}
          </div>
          <div className="text-xs text-fuchsia-600">Status: {email.status}</div>
        </div>
      ))}
    </div>
  );
};

// Email Accounts Component
const EmailAccounts = ({ accounts, onConnect }) => {
  return (
    <div className="space-y-3">
      {accounts.map(account => (
        <div key={account.id} className="border border-fuchsia-500 rounded p-3">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-fuchsia-400 font-medium">{account.email}</div>
              <div className="text-xs text-fuchsia-600">{account.provider}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded ${
                account.connected
                  ? 'bg-green-900/30 text-green-400'
                  : 'bg-red-900/30 text-red-400'
              }`}>
                {account.connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
              {!account.connected && (
                <button
                  onClick={() => onConnect(account.provider)}
                  className="px-2 py-1 bg-fuchsia-500 text-black rounded text-xs hover:bg-fuchsia-400"
                >
                  CONNECT
                </button>
              )}
            </div>
          </div>
        </div>
      ))}

      <div className="border-2 border-dashed border-fuchsia-500 rounded p-4 text-center">
        <div className="text-fuchsia-600 mb-2">Add New Email Account</div>
        <div className="flex gap-2 justify-center">
          <button
            onClick={() => onConnect('gmail')}
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-500"
          >
            Gmail
          </button>
          <button
            onClick={() => onConnect('outlook')}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-500"
          >
            Outlook
          </button>
        </div>
      </div>
    </div>
  );
};

// Email Composer Modal
const EmailComposer = ({ onClose, onSend, templates }) => {
  const [emailData, setEmailData] = useState({
    to: '',
    subject: '',
    body: '',
    account_id: ''
  });
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    if (!emailData.to || !emailData.subject || !emailData.body) {
      alert('Please fill in all required fields');
      return;
    }

    setIsSending(true);
    try {
      await onSend(emailData);
    } finally {
      setIsSending(false);
    }
  };

  const applyTemplate = (template) => {
    setEmailData({
      ...emailData,
      subject: template.subject,
      body: template.body
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-black border-2 border-fuchsia-500 rounded-lg w-full max-w-2xl mx-4 h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-fuchsia-500">
          <h3 className="text-lg font-bold text-fuchsia-500">COMPOSE EMAIL</h3>
          <button
            onClick={onClose}
            className="text-fuchsia-400 hover:text-fuchsia-300 text-xl"
          >
            ×
          </button>
        </div>

        {/* Templates */}
        <div className="px-4 py-2 border-b border-fuchsia-500">
          <div className="flex gap-2">
            <span className="text-sm text-fuchsia-600">Templates:</span>
            {templates.map(template => (
              <button
                key={template.id}
                onClick={() => applyTemplate(template)}
                className="text-xs px-2 py-1 bg-fuchsia-900/30 text-fuchsia-400 rounded hover:bg-fuchsia-800/30"
              >
                {template.name}
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="flex-1 p-4 space-y-4">
          <div>
            <label className="block text-sm text-fuchsia-400 mb-1">To:</label>
            <input
              type="email"
              value={emailData.to}
              onChange={(e) => setEmailData({...emailData, to: e.target.value})}
              className="w-full bg-black border border-fuchsia-500 rounded px-3 py-2 text-fuchsia-400 focus:outline-none focus:border-fuchsia-400"
              placeholder="recipient@example.com"
            />
          </div>

          <div>
            <label className="block text-sm text-fuchsia-400 mb-1">Subject:</label>
            <input
              type="text"
              value={emailData.subject}
              onChange={(e) => setEmailData({...emailData, subject: e.target.value})}
              className="w-full bg-black border border-fuchsia-500 rounded px-3 py-2 text-fuchsia-400 focus:outline-none focus:border-fuchsia-400"
              placeholder="Email subject..."
            />
          </div>

          <div className="flex-1">
            <label className="block text-sm text-fuchsia-400 mb-1">Message:</label>
            <textarea
              value={emailData.body}
              onChange={(e) => setEmailData({...emailData, body: e.target.value})}
              className="w-full bg-black border border-fuchsia-500 rounded px-3 py-2 text-fuchsia-400 focus:outline-none focus:border-fuchsia-400 h-40 resize-none"
              placeholder="Compose your message..."
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-4 border-t border-fuchsia-500">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-fuchsia-500 text-fuchsia-400 rounded hover:bg-fuchsia-500 hover:text-black transition-colors"
          >
            CANCEL
          </button>
          <button
            onClick={handleSend}
            disabled={isSending || !emailData.to || !emailData.subject || !emailData.body}
            className="px-4 py-2 bg-fuchsia-500 text-black rounded hover:bg-fuchsia-400 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isSending ? 'SENDING...' : 'SEND EMAIL'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommunicationPanel;