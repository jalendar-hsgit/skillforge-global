export const dynamic = 'force-dynamic'

import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { usePWA } from '@/hooks/usePWA';
import { apiGet, apiPut } from '@/lib/api';

interface NotificationPreferences {
  enabled: boolean;
  challenge_hints: boolean;
  submission_results: boolean;
  achievement_unlocked: boolean;
  daily_challenge: boolean;
  leaderboard_updates: boolean;
  contest_updates: boolean;
  social_notifications: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

interface PWAAnalytics {
  app_installed: boolean;
  total_sessions: number;
  total_offline_time_minutes: number;
  successful_syncs: number;
  failed_syncs: number;
  cache_hit_rate: number;
}

const PWASettingsPage: React.FC = () => {
  const {
    isOnline,
    isPWAInstalled,
    installPrompt,
    installPWA,
    requestNotificationPermission,
  } = usePWA();

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const [preferences, setPreferences] = useState<NotificationPreferences>({
    enabled: true,
    challenge_hints: true,
    submission_results: true,
    achievement_unlocked: true,
    daily_challenge: true,
    leaderboard_updates: false,
    contest_updates: true,
    social_notifications: true,
    quiet_hours_enabled: false,
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
  });

  const [analytics, setAnalytics] = useState<PWAAnalytics>({
    app_installed: false,
    total_sessions: 0,
    total_offline_time_minutes: 0,
    successful_syncs: 0,
    failed_syncs: 0,
    cache_hit_rate: 0,
  });

  // Fetch preferences
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [prefsRes, analyticsRes] = await Promise.all([
          apiGet('/api/v1x/pwa/notifications/preferences'),
          apiGet('/api/v1x/pwa/analytics'),
        ]);

        if (prefsRes.preferences) {
          setPreferences(prefsRes.preferences);
        }
        if (analyticsRes.analytics) {
          setAnalytics(analyticsRes.analytics);
        }
      } catch (err) {
        console.error('Failed to load PWA settings:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: any) => {
    setPreferences({
      ...preferences,
      [key]: value,
    });
  };

  const handleSavePreferences = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      await apiPut('/api/v1x/pwa/notifications/preferences', preferences);

      setSuccess('Notification preferences saved!');
    } catch (err: any) {
      setError(err.message || 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto py-12 text-center">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto py-12">
        <h1 className="text-4xl font-bold mb-8">App Settings</h1>

        {/* Status Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
            {success}
          </div>
        )}

        {/* Online Status */}
        <Card className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-2">Connection Status</h2>
              <p className="text-gray-600">Your current network status</p>
            </div>
            <div
              className={`px-4 py-2 rounded-lg font-semibold ${
                isOnline
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {isOnline ? '🌐 Online' : '📡 Offline'}
            </div>
          </div>
        </Card>

        {/* Install App */}
        {!isPWAInstalled && installPrompt && (
          <Card className="mb-6 bg-blue-50">
            <h2 className="text-xl font-bold mb-2">📱 Install App</h2>
            <p className="text-gray-700 mb-4">
              Install SkillForge Global on your device for offline access and better performance.
            </p>
            <Button onClick={installPWA} className="bg-blue-600 text-white">
              Install App
            </Button>
          </Card>
        )}

        {isPWAInstalled && (
          <Card className="mb-6 bg-green-50">
            <div className="flex items-center gap-3">
              <span className="text-3xl">✓</span>
              <div>
                <h3 className="font-bold text-green-800">App Installed</h3>
                <p className="text-sm text-green-700">
                  SkillForge Global is installed on your device
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Push Notifications */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold mb-6">🔔 Push Notifications</h2>

          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              Get notified when new challenges are available, you earn achievements, and more!
            </p>
            <Button
              onClick={requestNotificationPermission}
              className="mt-3 bg-blue-600 text-white"
            >
              Enable Notifications
            </Button>
          </div>

          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.enabled}
                onChange={(e) => handlePreferenceChange('enabled', e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded"
              />
              <span className="font-medium">Enable all notifications</span>
            </label>

            {preferences.enabled && (
              <>
                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.challenge_hints}
                    onChange={(e) => handlePreferenceChange('challenge_hints', e.target.checked)}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Challenge hints and tips</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.submission_results}
                    onChange={(e) => handlePreferenceChange('submission_results', e.target.checked)}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Submission results</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.achievement_unlocked}
                    onChange={(e) =>
                      handlePreferenceChange('achievement_unlocked', e.target.checked)
                    }
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Achievement unlocked</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.daily_challenge}
                    onChange={(e) => handlePreferenceChange('daily_challenge', e.target.checked)}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Daily challenge available</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.contest_updates}
                    onChange={(e) => handlePreferenceChange('contest_updates', e.target.checked)}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Contest updates</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-8">
                  <input
                    type="checkbox"
                    checked={preferences.social_notifications}
                    onChange={(e) =>
                      handlePreferenceChange('social_notifications', e.target.checked)
                    }
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span>Social interactions</span>
                </label>
              </>
            )}
          </div>
        </Card>

        {/* Quiet Hours */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold mb-6">🤫 Quiet Hours</h2>

          <label className="flex items-center gap-3 cursor-pointer mb-4">
            <input
              type="checkbox"
              checked={preferences.quiet_hours_enabled}
              onChange={(e) => handlePreferenceChange('quiet_hours_enabled', e.target.checked)}
              className="w-5 h-5 text-blue-600 rounded"
            />
            <span className="font-medium">Enable quiet hours</span>
          </label>

          {preferences.quiet_hours_enabled && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Start time</label>
                <input
                  type="time"
                  value={preferences.quiet_hours_start}
                  onChange={(e) =>
                    handlePreferenceChange('quiet_hours_start', e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">End time</label>
                <input
                  type="time"
                  value={preferences.quiet_hours_end}
                  onChange={(e) => handlePreferenceChange('quiet_hours_end', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
          )}
          <p className="text-sm text-gray-500 mt-3">
            Notifications will be silenced during these hours
          </p>
        </Card>

        {/* Save Preferences */}
        <Card className="mb-6 text-center">
          <Button onClick={handleSavePreferences} disabled={saving} className="px-8">
            {saving ? 'Saving...' : 'Save Preferences'}
          </Button>
        </Card>

        {/* Analytics */}
        <Card>
          <h2 className="text-2xl font-bold mb-6">📊 App Analytics</h2>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Sessions</p>
              <p className="text-2xl font-bold">{analytics.total_sessions}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Offline Time</p>
              <p className="text-2xl font-bold">{analytics.total_offline_time_minutes}m</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Successful Syncs</p>
              <p className="text-2xl font-bold">{analytics.successful_syncs}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Cache Hit Rate</p>
              <p className="text-2xl font-bold">{analytics.cache_hit_rate.toFixed(1)}%</p>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default PWASettingsPage;
