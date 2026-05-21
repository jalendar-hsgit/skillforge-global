import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { requireAdminSSR } from '@/lib/adminAuth';
import { GetServerSideProps } from 'next';

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  html_content: string;
  text_content: string;
  created_at: string;
}

interface NotificationRecord {
  id: number;
  subject: string;
  recipient_filter: string;
  recipient_count: number;
  sent_count: number;
  failed_count: number;
  sent_by: string;
  sent_at: string;
}

interface NotificationStats {
  total_notifications_sent: number;
  total_emails_sent: number;
  total_emails_failed: number;
  success_rate: number;
  recent_notifications: number;
  templates_count: number;
}

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState<'broadcast' | 'templates' | 'history'>('broadcast');
  
  // Broadcast state
  const [subject, setSubject] = useState('');
  const [htmlContent, setHtmlContent] = useState('');
  const [textContent, setTextContent] = useState('');
  const [recipientFilter, setRecipientFilter] = useState('all');
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<any>(null);
  
  // Templates state
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    subject: '',
    html_content: '',
    text_content: ''
  });
  
  // History state
  const [history, setHistory] = useState<NotificationRecord[]>([]);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  
  useEffect(() => {
    loadTemplates();
    loadHistory();
    loadStats();
  }, []);
  
  const loadTemplates = async () => {
    try {
      const res = await fetch('/api/admin/notifications/templates', {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };
  
  const loadHistory = async () => {
    try {
      const res = await fetch('/api/admin/notifications/history', {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.notifications || []);
      }
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };
  
  const loadStats = async () => {
    try {
      const res = await fetch('/api/admin/notifications/stats', {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };
  
  const handleSendBroadcast = async () => {
    if (!subject.trim() || !htmlContent.trim()) {
      alert('Please fill in subject and content');
      return;
    }
    
    setSending(true);
    setSendResult(null);
    
    try {
      const res = await fetch('/api/admin/notifications/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          subject,
          html_content: htmlContent,
          text_content: textContent || htmlContent.replace(/<[^>]*>/g, ''),
          recipient_filter: recipientFilter
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setSendResult(data);
        setSubject('');
        setHtmlContent('');
        setTextContent('');
        loadHistory();
        loadStats();
      } else {
        const error = await res.json();
        alert(`Error: ${error.detail || 'Failed to send broadcast'}`);
      }
    } catch (error) {
      console.error('Error sending broadcast:', error);
      alert('Failed to send broadcast');
    } finally {
      setSending(false);
    }
  };
  
  const handleUseTemplate = (template: EmailTemplate) => {
    setSubject(template.subject);
    setHtmlContent(template.html_content);
    setTextContent(template.text_content);
    setActiveTab('broadcast');
  };
  
  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    setTemplateForm({
      name: '',
      subject: '',
      html_content: '',
      text_content: ''
    });
    setShowTemplateModal(true);
  };
  
  const handleEditTemplate = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setTemplateForm({
      name: template.name,
      subject: template.subject,
      html_content: template.html_content,
      text_content: template.text_content
    });
    setShowTemplateModal(true);
  };
  
  const handleSaveTemplate = async () => {
    if (!templateForm.name.trim() || !templateForm.subject.trim()) {
      alert('Please fill in template name and subject');
      return;
    }
    
    try {
      const url = editingTemplate
        ? `/api/admin/notifications/templates/${editingTemplate.id}`
        : '/api/admin/notifications/templates';
      
      const res = await fetch(url, {
        method: editingTemplate ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(templateForm)
      });
      
      if (res.ok) {
        setShowTemplateModal(false);
        loadTemplates();
        loadStats();
      } else {
        const error = await res.json();
        alert(`Error: ${error.detail || 'Failed to save template'}`);
      }
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Failed to save template');
    }
  };
  
  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
      const res = await fetch(`/api/admin/notifications/templates/${templateId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (res.ok) {
        loadTemplates();
        loadStats();
      } else {
        const error = await res.json();
        alert(`Error: ${error.detail || 'Failed to delete template'}`);
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Failed to delete template');
    }
  };
  
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Email & Notifications</h1>
          <p className="mt-2 text-gray-600">Send broadcast emails and manage templates</p>
        </div>
        
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Total Sent</div>
              <div className="text-2xl font-bold">{stats.total_notifications_sent}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Emails Delivered</div>
              <div className="text-2xl font-bold text-green-600">{stats.total_emails_sent}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Failed</div>
              <div className="text-2xl font-bold text-red-600">{stats.total_emails_failed}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Success Rate</div>
              <div className="text-2xl font-bold">{stats.success_rate}%</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Recent (7d)</div>
              <div className="text-2xl font-bold">{stats.recent_notifications}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-500">Templates</div>
              <div className="text-2xl font-bold">{stats.templates_count}</div>
            </div>
          </div>
        )}
        
        {/* Tabs */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('broadcast')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'broadcast'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Broadcast Email
              </button>
              <button
                onClick={() => setActiveTab('templates')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'templates'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Templates ({templates.length})
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-6 py-3 text-sm font-medium border-b-2 ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                History ({history.length})
              </button>
            </nav>
          </div>
          
          <div className="p-6">
            {/* Broadcast Tab */}
            {activeTab === 'broadcast' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Send Broadcast Email</h2>
                
                {sendResult && (
                  <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-green-800 font-semibold">✓ Broadcast sent successfully!</p>
                    <p className="text-sm text-green-700 mt-1">
                      Sent to {sendResult.sent_count} recipients
                      {sendResult.failed_count > 0 && ` (${sendResult.failed_count} failed)`}
                    </p>
                  </div>
                )}
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Recipient Filter
                    </label>
                    <select
                      value={recipientFilter}
                      onChange={(e) => setRecipientFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="all">All Users</option>
                      <option value="students">Students Only</option>
                      <option value="mentors">Mentors Only</option>
                      <option value="at_risk">At-Risk Users (Inactive 30+ days)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subject
                    </label>
                    <input
                      type="text"
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="Email subject line"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      HTML Content
                    </label>
                    <textarea
                      value={htmlContent}
                      onChange={(e) => setHtmlContent(e.target.value)}
                      rows={10}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                      placeholder="<h1>Hello!</h1><p>Your message here...</p>"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Plain Text Content (Optional)
                    </label>
                    <textarea
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="Plain text version (auto-generated if left empty)"
                    />
                  </div>
                  
                  <div className="flex gap-3">
                    <button
                      onClick={handleSendBroadcast}
                      disabled={sending}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {sending ? 'Sending...' : 'Send Broadcast'}
                    </button>
                    <button
                      onClick={() => {
                        setSubject('');
                        setHtmlContent('');
                        setTextContent('');
                        setSendResult(null);
                      }}
                      className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </div>
            )}
            
            {/* Templates Tab */}
            {activeTab === 'templates' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Email Templates</h2>
                  <button
                    onClick={handleCreateTemplate}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    + New Template
                  </button>
                </div>
                
                {templates.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No templates yet. Create one to get started!
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {templates.map((template) => (
                      <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                        <h3 className="font-semibold text-lg mb-2">{template.name}</h3>
                        <p className="text-sm text-gray-600 mb-3">Subject: {template.subject}</p>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleUseTemplate(template)}
                            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                          >
                            Use Template
                          </button>
                          <button
                            onClick={() => handleEditTemplate(template)}
                            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteTemplate(template.id)}
                            className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* History Tab */}
            {activeTab === 'history' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Notification History</h2>
                
                {history.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    No notifications sent yet
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Subject</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Filter</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Recipients</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Sent</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Failed</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Sent By</th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Date</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {history.map((record) => (
                          <tr key={record.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm">{record.subject}</td>
                            <td className="px-4 py-3 text-sm">
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                {record.recipient_filter}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm">{record.recipient_count}</td>
                            <td className="px-4 py-3 text-sm text-green-600">{record.sent_count}</td>
                            <td className="px-4 py-3 text-sm text-red-600">{record.failed_count}</td>
                            <td className="px-4 py-3 text-sm">{record.sent_by}</td>
                            <td className="px-4 py-3 text-sm text-gray-500">
                              {new Date(record.sent_at).toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Template Modal */}
        {showTemplateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-semibold mb-4">
                {editingTemplate ? 'Edit Template' : 'New Template'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Template Name
                  </label>
                  <input
                    type="text"
                    value={templateForm.name}
                    onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    placeholder="e.g., Welcome Email, Re-engagement Campaign"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={templateForm.subject}
                    onChange={(e) => setTemplateForm({ ...templateForm, subject: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    HTML Content
                  </label>
                  <textarea
                    value={templateForm.html_content}
                    onChange={(e) => setTemplateForm({ ...templateForm, html_content: e.target.value })}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Plain Text Content
                  </label>
                  <textarea
                    value={templateForm.text_content}
                    onChange={(e) => setTemplateForm({ ...templateForm, text_content: e.target.value })}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              
              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleSaveTemplate}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Template
                </button>
                <button
                  onClick={() => setShowTemplateModal(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export const getServerSideProps: GetServerSideProps = requireAdminSSR;
