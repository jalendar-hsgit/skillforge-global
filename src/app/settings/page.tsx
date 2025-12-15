/**
 * User Settings Page
 * Manage profile, preferences, and account settings
 */

'use client';

import React, { useState, useEffect } from 'react';

interface UserProfile {
  bio?: string;
  location?: string;
  company?: string;
  job_title?: string;
  website?: string;
  avatar_url?: string;
  theme_preference?: string;
  preferred_language?: string;
  is_public?: boolean;
}

interface UserPreferences {
  notifications: {
    challenge_reminders: boolean;
    streak_achievements: boolean;
    solution_votes: boolean;
    comments: boolean;
    friend_activity: boolean;
  };
  learning: {
    preferred_difficulty: string;
    show_hints_automatically: boolean;
    daily_challenge_enabled: boolean;
  };
  privacy: {
    allow_tracking: boolean;
  };
}

export default function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile>({});
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'privacy'>('profile');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      const profileRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/me`,
        { credentials: 'include' }
      );
      
      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile({
          bio: profileData.bio,
          location: profileData.location,
          company: profileData.company,
          job_title: profileData.job_title,
          website: profileData.website,
          avatar_url: profileData.avatar_url,
          theme_preference: profileData.theme_preference,
          preferred_language: profileData.preferred_language,
          is_public: profileData.is_public,
        });
      }

      const prefsRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/preferences`,
        { credentials: 'include' }
      );
      
      if (prefsRes.ok) {
        const prefsData = await prefsRes.json();
        setPreferences(prefsData);
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
      setMessage({ type: 'error', text: 'Failed to load settings' });
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      setSaving(true);
      
      const params = new URLSearchParams();
      if (profile.bio) params.append('bio', profile.bio);
      if (profile.location) params.append('location', profile.location);
      if (profile.company) params.append('company', profile.company);
      if (profile.job_title) params.append('job_title', profile.job_title);
      if (profile.website) params.append('website', profile.website);
      if (profile.avatar_url) params.append('avatar_url', profile.avatar_url);
      if (profile.theme_preference) params.append('theme_preference', profile.theme_preference);
      if (profile.preferred_language) params.append('preferred_language', profile.preferred_language);
      if (profile.is_public !== undefined) params.append('is_public', profile.is_public.toString());

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/me`,
        {
          method: 'PUT',
          body: params,
          credentials: 'include',
        }
      );

      if (res.ok) {
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
      } else {
        setMessage({ type: 'error', text: 'Failed to update profile' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Error updating profile' });
    } finally {
      setSaving(false);
    }
  };

  const handlePreferencesUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!preferences) return;

    try {
      setSaving(true);
      
      const params = new URLSearchParams();
      params.append('notify_challenge_reminders', preferences.notifications.challenge_reminders.toString());
      params.append('notify_streak_achievements', preferences.notifications.streak_achievements.toString());
      params.append('notify_solution_votes', preferences.notifications.solution_votes.toString());
      params.append('notify_comments', preferences.notifications.comments.toString());
      params.append('notify_friend_activity', preferences.notifications.friend_activity.toString());
      params.append('preferred_difficulty', preferences.learning.preferred_difficulty);
      params.append('show_hints_automatically', preferences.learning.show_hints_automatically.toString());
      params.append('daily_challenge_enabled', preferences.learning.daily_challenge_enabled.toString());
      params.append('allow_tracking', preferences.privacy.allow_tracking.toString());

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1x/profiles/preferences`,
        {
          method: 'PUT',
          body: params,
          credentials: 'include',
        }
      );

      if (res.ok) {
        setMessage({ type: 'success', text: 'Preferences updated successfully!' });
      } else {
        setMessage({ type: 'error', text: 'Failed to update preferences' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Error updating preferences' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        {message && (
          <div
            className={`mb-6 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6 border-b border-gray-200">
          {(['profile', 'preferences', 'privacy'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 px-4 font-medium transition-colors ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <form onSubmit={handleProfileUpdate} className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Profile Information</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bio
                  </label>
                  <textarea
                    value={profile.bio || ''}
                    onChange={e => setProfile({ ...profile, bio: e.target.value })}
                    placeholder="Tell us about yourself..."
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    value={profile.location || ''}
                    onChange={e => setProfile({ ...profile, location: e.target.value })}
                    placeholder="City, Country"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    value={profile.company || ''}
                    onChange={e => setProfile({ ...profile, company: e.target.value })}
                    placeholder="Your company"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title
                  </label>
                  <input
                    type="text"
                    value={profile.job_title || ''}
                    onChange={e => setProfile({ ...profile, job_title: e.target.value })}
                    placeholder="Your position"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Website
                  </label>
                  <input
                    type="url"
                    value={profile.website || ''}
                    onChange={e => setProfile({ ...profile, website: e.target.value })}
                    placeholder="https://example.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Language
                  </label>
                  <select
                    value={profile.preferred_language || 'python'}
                    onChange={e => setProfile({ ...profile, preferred_language: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="csharp">C#</option>
                    <option value="go">Go</option>
                    <option value="rust">Rust</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.is_public !== false}
                    onChange={e => setProfile({ ...profile, is_public: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">Make my profile public</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
            </form>
          )}

          {/* Preferences Tab */}
          {activeTab === 'preferences' && preferences && (
            <form onSubmit={handlePreferencesUpdate} className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Preferences</h2>

              <div>
                <h3 className="font-bold text-gray-900 mb-3">Notifications</h3>
                <div className="space-y-3">
                  {[
                    { key: 'challenge_reminders', label: 'Challenge reminders' },
                    { key: 'streak_achievements', label: 'Streak achievements' },
                    { key: 'solution_votes', label: 'Solution votes' },
                    { key: 'comments', label: 'Comments on my solutions' },
                    { key: 'friend_activity', label: 'Friend activity' },
                  ].map(({ key, label }) => (
                    <label key={key} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.notifications[key as keyof typeof preferences.notifications] as boolean}
                        onChange={e =>
                          setPreferences({
                            ...preferences,
                            notifications: {
                              ...preferences.notifications,
                              [key]: e.target.checked,
                            },
                          })
                        }
                        className="w-4 h-4"
                      />
                      <span className="text-sm text-gray-700">{label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="font-bold text-gray-900 mb-3">Learning</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-2">
                      Preferred Difficulty
                    </label>
                    <select
                      value={preferences.learning.preferred_difficulty}
                      onChange={e =>
                        setPreferences({
                          ...preferences,
                          learning: { ...preferences.learning, preferred_difficulty: e.target.value },
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>

                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.learning.show_hints_automatically}
                      onChange={e =>
                        setPreferences({
                          ...preferences,
                          learning: { ...preferences.learning, show_hints_automatically: e.target.checked },
                        })
                      }
                      className="w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">Show hints automatically</span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.learning.daily_challenge_enabled}
                      onChange={e =>
                        setPreferences({
                          ...preferences,
                          learning: { ...preferences.learning, daily_challenge_enabled: e.target.checked },
                        })
                      }
                      className="w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">Enable daily challenges</span>
                  </label>
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Preferences'}
              </button>
            </form>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && preferences && (
            <form onSubmit={handlePreferencesUpdate} className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Privacy & Security</h2>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.privacy.allow_tracking}
                  onChange={e =>
                    setPreferences({
                      ...preferences,
                      privacy: { ...preferences.privacy, allow_tracking: e.target.checked },
                    })
                  }
                  className="w-4 h-4"
                />
                <div>
                  <span className="text-sm text-gray-700 block">Allow analytics tracking</span>
                  <span className="text-xs text-gray-600">Help us improve by sharing anonymized usage data</span>
                </div>
              </label>

              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
