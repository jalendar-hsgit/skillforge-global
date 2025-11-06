import { useState, useEffect } from 'react';
import { X, Linkedin, CheckCircle, AlertCircle, Loader, ExternalLink, RefreshCw } from 'lucide-react';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

interface LinkedInStatus {
  connected: boolean;
  expired?: boolean;
  profile_url: string | null;
  last_import: string | null;
  import_count: number;
}

interface LinkedInImportModalProps {
  resumeId?: number;
  isOpen: boolean;
  onClose: () => void;
  onImportComplete?: (resumeId: number) => void;
}

export default function LinkedInImportModal({ resumeId, isOpen, onClose, onImportComplete }: LinkedInImportModalProps) {
  const [status, setStatus] = useState<LinkedInStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [createNew, setCreateNew] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen]);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/linkedin-import/status`, {
        credentials: 'include'
      });
      
      if (!response.ok) throw new Error('Failed to fetch status');
      
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Error fetching LinkedIn status:', err);
    }
  };

  const handleConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1x/linkedin-import/auth`, {
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Failed to initiate LinkedIn auth');

      const data = await response.json();
      
      // Open LinkedIn OAuth in popup
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;
      
      const popup = window.open(
        data.auth_url,
        'LinkedIn Login',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      // Poll for popup closure or success
      const checkPopup = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkPopup);
          fetchStatus(); // Refresh status after auth
          setLoading(false);
        }
      }, 1000);

    } catch (err) {
      console.error('Error connecting LinkedIn:', err);
      setError('Failed to connect LinkedIn account');
      setLoading(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1x/linkedin-import/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          create_new_resume: createNew,
          resume_id: !createNew ? resumeId : null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to import profile');
      }

      const data = await response.json();
      setSuccess(data.message);
      
      if (onImportComplete) {
        onImportComplete(data.resume_id);
      }

      // Close modal after 2 seconds
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (err: any) {
      console.error('Error importing LinkedIn profile:', err);
      setError(err.message || 'Failed to import LinkedIn profile');
    } finally {
      setImporting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your LinkedIn account?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1x/linkedin-import/disconnect`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Failed to disconnect');

      setStatus(null);
      setSuccess('LinkedIn account disconnected');
    } catch (err) {
      console.error('Error disconnecting LinkedIn:', err);
      setError('Failed to disconnect LinkedIn account');
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1x/linkedin-import/refresh-profile`, {
        method: 'POST',
        credentials: 'include'
      });

      if (!response.ok) throw new Error('Failed to refresh profile');

      setSuccess('Profile refreshed successfully');
      fetchStatus();
    } catch (err: any) {
      console.error('Error refreshing profile:', err);
      setError(err.message || 'Failed to refresh profile');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden border border-gray-200 animate-scale-in">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-[#0077B5] to-[#005885] px-6 py-5 flex items-center justify-between z-10 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center shadow-glass">
              <Linkedin className="w-7 h-7 text-white drop-shadow-lg" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight drop-shadow-md">LinkedIn Import</h2>
              <p className="text-sm text-white/90 font-medium">Connect and import your LinkedIn profile</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-white/80 hover:text-white transition-all duration-200 hover:bg-white/20 rounded-lg p-2"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="overflow-y-auto max-h-[calc(90vh-88px)]">

        <div className="p-6 space-y-6">
          {error && (
            <div className="mb-4 p-4 bg-gradient-to-r from-red-50 to-red-100 border-l-4 border-red-500 rounded-xl text-red-800 shadow-sm animate-slide-down flex items-start gap-3">
              <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <p className="font-semibold">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 p-4 bg-gradient-to-r from-green-50 to-emerald-100 border-l-4 border-green-500 rounded-xl text-green-800 shadow-sm animate-slide-down flex items-start gap-3">
              <CheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <p className="font-semibold">{success}</p>
            </div>
          )}

          {!status?.connected ? (
            /* Not Connected View */
            <div className="text-center py-10 animate-slide-up">
              <div className="w-24 h-24 bg-gradient-to-br from-[#0077B5] to-[#005885] bg-opacity-10 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Linkedin className="w-12 h-12 text-[#0077B5]" />
              </div>
              
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Connect Your LinkedIn Account
              </h3>
              
              <p className="text-gray-600 mb-8 max-w-md mx-auto leading-relaxed text-lg">
                Instantly populate your resume with your LinkedIn profile data. 
                We'll import your work experience, education, skills, and more.
              </p>

              <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-blue-50 border-2 border-blue-200 rounded-2xl p-6 mb-8 text-left shadow-lg">
                <h4 className="font-bold text-gray-900 mb-4 text-lg flex items-center gap-2">
                  <span className="text-[#0077B5]">✓</span>
                  What we'll import:
                </h4>
                <ul className="space-y-3 text-sm text-gray-700">
                  <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/50 transition-colors">
                    <div className="p-1.5 bg-blue-100 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Contact information</span>
                  </li>
                  <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/50 transition-colors">
                    <div className="p-1.5 bg-blue-100 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Professional headline</span>
                  </li>
                  <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/50 transition-colors">
                    <div className="p-1.5 bg-blue-100 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Work experience history</span>
                  </li>
                  <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/50 transition-colors">
                    <div className="p-1.5 bg-blue-100 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Education details</span>
                  </li>
                  <li className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/50 transition-colors">
                    <div className="p-1.5 bg-blue-100 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Skills and endorsements</span>
                  </li>
                </ul>
              </div>

              <Button
                onClick={handleConnect}
                disabled={loading}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-[#0077B5] to-[#005885] hover:from-[#005885] hover:to-[#003d5c] text-white font-bold py-4 px-8 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-6 h-6 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Linkedin className="w-6 h-6" />
                    Connect with LinkedIn
                  </>
                )}
              </Button>

              <p className="text-sm text-gray-500 mt-6 italic flex items-center justify-center gap-2">
                <span className="text-green-600">🔒</span>
                We respect your privacy. Your LinkedIn data is encrypted and never shared.
              </p>
            </div>
          ) : (
            /* Connected View */
            <div className="animate-slide-up">
              {/* Connection Status */}
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-xl p-5 mb-6 shadow-md">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-green-900 mb-2 text-lg">LinkedIn Connected</h4>
                    <div className="space-y-2">
                      {status.profile_url && (
                        <a 
                          href={status.profile_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-green-700 hover:text-green-800 font-semibold hover:underline transition-colors"
                        >
                          View Profile
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                      {status.last_import && (
                        <p className="text-sm text-green-700">
                          <span className="font-semibold">Last import:</span> {new Date(status.last_import).toLocaleDateString()}
                        </p>
                      )}
                      <p className="text-sm text-green-700">
                        <span className="font-semibold">Total imports:</span> {status.import_count}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {status.expired && (
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-500 rounded-xl p-5 mb-6 shadow-md animate-slide-down">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <AlertCircle className="w-6 h-6 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-yellow-900 mb-2 text-lg">Token Expired</h4>
                      <p className="text-sm text-yellow-800 mb-4 leading-relaxed">
                        Your LinkedIn connection has expired. Please reconnect to import data.
                      </p>
                      <Button 
                        onClick={handleConnect} 
                        className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-semibold px-6 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all"
                      >
                        Reconnect LinkedIn
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {!status.expired && (
                <>
                  {/* Import Options */}
                  <div className="mb-6">
                    <h4 className="font-medium text-gray-900 mb-3">Import Options</h4>
                    
                    <div className="space-y-3">
                      <label className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name="import-mode"
                          checked={createNew}
                          onChange={() => setCreateNew(true)}
                          className="mt-1"
                        />
                        <div>
                          <p className="font-medium text-gray-900">Create New Resume</p>
                          <p className="text-sm text-gray-600">
                            Import as a brand new resume
                          </p>
                        </div>
                      </label>

                      <label className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          name="import-mode"
                          checked={!createNew}
                          onChange={() => setCreateNew(false)}
                          className="mt-1"
                          disabled={!resumeId}
                        />
                        <div>
                          <p className="font-medium text-gray-900">Update Current Resume</p>
                          <p className="text-sm text-gray-600">
                            Merge LinkedIn data into the current resume
                          </p>
                          {!resumeId && (
                            <p className="text-xs text-red-600 mt-1">
                              No resume selected
                            </p>
                          )}
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <Button
                      onClick={handleImport}
                      disabled={importing}
                      className="flex-1"
                    >
                      {importing ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin mr-2" />
                          Importing...
                        </>
                      ) : (
                        'Import Profile Data'
                      )}
                    </Button>

                    <Button
                      onClick={handleRefresh}
                      disabled={loading}
                      variant="outline"
                    >
                      Refresh
                    </Button>
                  </div>

                  {/* Disconnect Option */}
                  <div className="mt-6 pt-6 border-t">
                    <button
                      onClick={handleDisconnect}
                      className="text-sm text-red-600 hover:text-red-700 hover:underline"
                    >
                      Disconnect LinkedIn Account
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  );
}
