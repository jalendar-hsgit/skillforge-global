import React, { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiCall } from '@/lib/api';

interface HintPreferences {
  id: number;
  userId: number;
  hintsQuotaPerDay: number;
  hintsQuotaPerMonth: number;
  preferredHintType: string;
  preferredDifficulty: string;
  includeCodeExamples: boolean;
  includeResources: boolean;
  showAllHints: boolean;
  enableNotifications: boolean;
}

const HintPreferencesPage: React.FC = () => {
  const [preferences, setPreferences] = useState<HintPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    hintsQuotaPerDay: 5,
    hintsQuotaPerMonth: 50,
    preferredHintType: 'approach_suggestion',
    preferredDifficulty: 'moderate',
    includeCodeExamples: true,
    includeResources: true,
    showAllHints: false,
    enableNotifications: true,
  });

  // Fetch preferences on mount
  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const data = await apiCall('/api/v1x/hints/preferences', {
        method: 'GET',
      });

      if (data.preferences) {
        setPreferences(data.preferences);
        setFormData({
          hintsQuotaPerDay: data.preferences.hintsQuotaPerDay || 5,
          hintsQuotaPerMonth: data.preferences.hintsQuotaPerMonth || 50,
          preferredHintType: data.preferences.preferredHintType || 'approach_suggestion',
          preferredDifficulty: data.preferences.preferredDifficulty || 'moderate',
          includeCodeExamples: data.preferences.includeCodeExamples !== false,
          includeResources: data.preferences.includeResources !== false,
          showAllHints: data.preferences.showAllHints || false,
          enableNotifications: data.preferences.enableNotifications !== false,
        });
      }
    } catch (err) {
      setError('Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const inputElement = e.target as HTMLInputElement;
    
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? inputElement.checked : value,
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const data = await apiCall('/api/v1x/hints/preferences', {
        method: 'PUT',
        body: JSON.stringify(formData),
      });

      if (data.success) {
        setSuccess('Preferences saved successfully!');
        fetchPreferences();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto py-12">
          <div className="text-center">Loading preferences...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Hint Preferences</h1>
          <p className="text-gray-600">Customize how you receive AI hints</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
            {success}
          </div>
        )}

        {/* Daily & Monthly Quotas */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold mb-6">Hint Quotas</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">
                Daily Hint Limit
              </label>
              <input
                type="number"
                name="hintsQuotaPerDay"
                min="1"
                max="20"
                value={formData.hintsQuotaPerDay}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">How many hints you can request per day</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">
                Monthly Hint Limit
              </label>
              <input
                type="number"
                name="hintsQuotaPerMonth"
                min="10"
                max="500"
                value={formData.hintsQuotaPerMonth}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">How many hints you can request per month</p>
            </div>
          </div>

          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-sm text-blue-900">
              💡 <strong>Premium users</strong> get unlimited hints. Adjust these limits to match your learning style.
            </p>
          </div>
        </Card>

        {/* Hint Content Preferences */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold mb-6">Hint Content</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">
                Preferred Hint Type
              </label>
              <select
                name="preferredHintType"
                value={formData.preferredHintType}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="concept_explanation">Concept Explanation</option>
                <option value="approach_suggestion">Approach Suggestion</option>
                <option value="step_by_step">Step by Step</option>
                <option value="common_mistakes">Common Mistakes</option>
                <option value="edge_cases">Edge Cases</option>
                <option value="code_pattern">Code Pattern</option>
                <option value="debugging_hint">Debugging Hint</option>
                <option value="optimization_hint">Optimization Hint</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Your default hint type for new challenges</p>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2 text-gray-700">
                Preferred Difficulty Level
              </label>
              <select
                name="preferredDifficulty"
                value={formData.preferredDifficulty}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="very_easy">Very Easy (Lots of guidance)</option>
                <option value="easy">Easy (Some guidance)</option>
                <option value="moderate">Moderate (Balanced)</option>
                <option value="hard">Hard (Minimal guidance)</option>
                <option value="very_hard">Very Hard (Just a nudge)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">How detailed your hints should be</p>
            </div>
          </div>

          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="includeCodeExamples"
                checked={formData.includeCodeExamples}
                onChange={handleChange}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-gray-800 font-medium">Include Code Examples</span>
              <span className="text-xs text-gray-500">(Working code snippets with hints)</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="includeResources"
                checked={formData.includeResources}
                onChange={handleChange}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-gray-800 font-medium">Include Learning Resources</span>
              <span className="text-xs text-gray-500">(Links to docs, tutorials, etc.)</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="showAllHints"
                checked={formData.showAllHints}
                onChange={handleChange}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-gray-800 font-medium">Show All Available Hints</span>
              <span className="text-xs text-gray-500">(See multiple hint options, then choose)</span>
            </label>
          </div>
        </Card>

        {/* Notifications */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold mb-6">Notifications</h2>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              name="enableNotifications"
              checked={formData.enableNotifications}
              onChange={handleChange}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <div>
              <span className="text-gray-800 font-medium">Enable Hint Notifications</span>
              <p className="text-xs text-gray-500">Get notified when new high-quality hints are available</p>
            </div>
          </label>
        </Card>

        {/* Save Button */}
        <Card className="text-center">
          <Button
            onClick={handleSave}
            disabled={saving}
            className="px-8 py-3"
          >
            {saving ? 'Saving...' : 'Save Preferences'}
          </Button>
          <p className="text-sm text-gray-500 mt-4">
            Changes are saved to your account and apply immediately
          </p>
        </Card>

        {/* Info Section */}
        <Card className="mt-8 bg-blue-50">
          <h3 className="text-lg font-bold mb-3 text-blue-900">💡 About Hint Preferences</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>✓ <strong>Quotas</strong> determine how many hints you can use daily/monthly</li>
            <li>✓ <strong>Content options</strong> let you customize the style and depth of hints</li>
            <li>✓ <strong>Code examples</strong> provide working implementations to learn from</li>
            <li>✓ <strong>Resources</strong> link to relevant documentation and tutorials</li>
            <li>✓ <strong>Show all hints</strong> lets you see multiple options instead of one random hint</li>
            <li>✓ Premium users can enjoy <strong>unlimited hints</strong> with no daily/monthly limits</li>
          </ul>
        </Card>
      </div>
    </Layout>
  );
};

export default HintPreferencesPage;
