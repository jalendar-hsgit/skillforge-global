import { useEffect, useState } from 'react'
import { LogOut, Smartphone, Monitor, AlertCircle } from 'lucide-react'

interface LoginRecord {
  id: number
  timestamp: string
  device: string
  browser: string
  ip_address: string
  location: string
  is_current: boolean
  is_suspicious: boolean
}

export default function LoginHistory() {
  const [logins, setLogins] = useState<LoginRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadLoginHistory()
  }, [])

  async function loadLoginHistory() {
    setLoading(true)
    try {
      const response = await fetch('/api/v1x/auth/login-history', {
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to load login history')
      }

      const data = await response.json()
      setLogins(data.logins || [])
    } catch (err: any) {
      setError(err?.message || 'Failed to load login history')
    } finally {
      setLoading(false)
    }
  }

  async function handleRevokeSession(loginId: number) {
    try {
      const response = await fetch(`/api/v1x/auth/login-history/${loginId}/revoke`, {
        method: 'POST',
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Failed to revoke session')
      }

      // Reload history
      loadLoginHistory()
    } catch (err: any) {
      setError(err?.message || 'Failed to revoke session')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const getDeviceIcon = (device: string) => {
    if (device.toLowerCase().includes('mobile')) {
      return <Smartphone className="w-5 h-5 text-blue-600" />
    }
    return <Monitor className="w-5 h-5 text-gray-600" />
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays < 7) return `${diffDays} days ago`
    
    return date.toLocaleDateString()
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-bold text-gray-900">Login History</h2>
        <p className="text-sm text-gray-600 mt-1">
          Active sessions and recent logins on your account
        </p>
      </div>

      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <div className="divide-y divide-gray-200">
        {logins && logins.length > 0 ? (
          logins.map((login) => (
            <div key={login.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  {/* Device Icon */}
                  <div className="mt-1">
                    {getDeviceIcon(login.device)}
                  </div>

                  {/* Login Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-gray-900">
                        {login.browser || 'Unknown Browser'}
                      </p>
                      {login.is_current && (
                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                          Current Session
                        </span>
                      )}
                      {login.is_suspicious && (
                        <span className="inline-block px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          Suspicious
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-600">
                      {login.device} • {login.location || 'Unknown location'}
                    </p>

                    <p className="text-xs text-gray-500 mt-2">
                      IP: {login.ip_address}
                    </p>

                    <p className="text-xs text-gray-500 mt-1">
                      {formatTime(login.timestamp)}
                    </p>
                  </div>
                </div>

                {/* Revoke Button */}
                {!login.is_current && (
                  <button
                    onClick={() => handleRevokeSession(login.id)}
                    className="ml-4 text-red-600 hover:text-red-800 font-medium text-sm flex items-center gap-1 py-2 px-3 rounded hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Revoke
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="p-6 text-center text-gray-500">
            <p>No login history found</p>
          </div>
        )}
      </div>

      {logins && logins.length > 0 && (
        <div className="p-4 bg-blue-50 border-t border-gray-200">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">Security Tip:</span> Regularly review your active sessions. 
            If you see a session you don't recognize, revoke it immediately and change your password.
          </p>
        </div>
      )}
    </div>
  )
}
