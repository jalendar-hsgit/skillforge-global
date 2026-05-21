import { useState } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface Achievement {
  id: number;
  title: string;
  description: string;
  date?: string;
}

interface AchievementsSectionProps {
  resumeId: number;
  achievements: Achievement[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function AchievementsSection({
  resumeId,
  achievements,
  onUpdate,
}: AchievementsSectionProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleAdd = () => {
    setEditingId(null);
    setShowForm(true);
  };

  const handleEdit = (id: number) => {
    setEditingId(id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this achievement?')) return;

    try {
      const response = await fetch(
        `/api/session/v1x/achievements?id=${id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting achievement:', error);
      alert('Failed to delete achievement');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent tracking-tight">Achievements & Awards</h2>
          <p className="text-techGray/80 mt-1">
            Highlight your accomplishments, awards, and recognitions.
          </p>
        </div>
        <Button onClick={handleAdd} variant="primary">
          + Add Achievement
        </Button>
      </div>

      {achievements.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">⭐</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No achievements yet</h3>
          <p className="text-gray-600 mb-4">
            Showcase awards, recognitions, and notable accomplishments.
          </p>
          <Button onClick={handleAdd} variant="primary">
            Add Achievement
          </Button>
        </Card>
      )}

      {achievements.map((achievement) => (
        <Card key={achievement.id} className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{achievement.title}</h3>
              {achievement.date && (
                <p className="text-sm text-gray-500 mt-1">{achievement.date}</p>
              )}
              <p className="text-sm text-gray-700 mt-2">{achievement.description}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(achievement.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(achievement.id)}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </Card>
      ))}

      {showForm && (
        <AchievementForm
          resumeId={resumeId}
          achievementId={editingId}
          onClose={() => {
            setShowForm(false);
            setEditingId(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingId(null);
            onUpdate();
          }}
        />
      )}

      {/* Pro Tips (screen only) */}
      {achievements.length > 0 && (
        <Card className="p-4 bg-blue-50 border-blue-200 print:hidden">
          <h4 className="font-semibold text-gray-900 mb-2">💡 Pro Tips:</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Include quantifiable metrics (e.g., "increased sales by 40%")</li>
            <li>• Highlight achievements relevant to your target role</li>
            <li>• Keep descriptions concise but impactful</li>
            <li>• Include awards from work, school, or industry organizations</li>
          </ul>
        </Card>
      )}
    </div>
  );
}

// Form Component
interface AchievementFormProps {
  resumeId: number;
  achievementId: number | null;
  onClose: () => void;
  onSave: () => void;
}

function AchievementForm({ resumeId, achievementId, onClose, onSave }: AchievementFormProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const url = achievementId
        ? `/api/session/v1x/achievements?id=${achievementId}`
        : `/api/session/v1x/achievements?resumeId=${resumeId}`;

      const response = await fetch(url, {
        method: achievementId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to save achievement');
      }
    } catch (error) {
      console.error('Error saving achievement:', error);
      alert('Failed to save achievement');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {achievementId ? 'Edit' : 'Add'} Achievement
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.title}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, title: e.target.value })
            }
            placeholder="Employee of the Year"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
            placeholder="Describe the achievement and its impact..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Date (Optional)</label>
          <Input
            type="month"
            value={formData.date}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, date: e.target.value })
            }
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="submit" variant="primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
          <Button type="button" onClick={onClose} variant="secondary">
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}
