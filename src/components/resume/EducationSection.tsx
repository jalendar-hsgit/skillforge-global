import { useState } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface Education {
  id: number;
  school: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  gpa?: string;
  achievements?: string[];
}

interface EducationSectionProps {
  resumeId: number;
  education: Education[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function EducationSection({
  resumeId,
  education,
  onUpdate,
}: EducationSectionProps) {
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
    if (!confirm('Are you sure you want to delete this education?')) return;

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(
        `${API_BASE}/api/v1x/resumes/${resumeId}/education/${id}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting education:', error);
      alert('Failed to delete education');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Education</h2>
          <p className="text-gray-600 mt-1">
            List your academic background, starting with the most recent.
          </p>
        </div>
        <Button onClick={handleAdd} variant="primary">
          + Add Education
        </Button>
      </div>

      {education.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🎓</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No education yet</h3>
          <p className="text-gray-600 mb-4">Start by adding your highest degree.</p>
          <Button onClick={handleAdd} variant="primary">
            Add Education
          </Button>
        </Card>
      )}

      {education.map((edu) => (
        <Card key={edu.id} className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                {edu.degree} in {edu.field_of_study}
              </h3>
              <p className="text-md text-gray-700 font-medium">{edu.school}</p>
              <p className="text-sm text-gray-500 mt-1">
                {edu.start_date} - {edu.is_current ? 'Present' : edu.end_date || 'Present'}
              </p>
              {edu.gpa && (
                <p className="text-sm text-gray-600 mt-1">GPA: {edu.gpa}</p>
              )}
              {edu.achievements && edu.achievements.length > 0 && (
                <ul className="mt-3 space-y-1">
                  {edu.achievements.map((achievement, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{achievement}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(edu.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(edu.id)}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </Card>
      ))}

      {showForm && (
        <EducationForm
          resumeId={resumeId}
          educationId={editingId}
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
    </div>
  );
}

// Form Component
interface EducationFormProps {
  resumeId: number;
  educationId: number | null;
  onClose: () => void;
  onSave: () => void;
}

function EducationForm({ resumeId, educationId, onClose, onSave }: EducationFormProps) {
  const [formData, setFormData] = useState({
    school: '',
    degree: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    is_current: false,
    gpa: '',
    achievements: [''],
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const url = educationId
        ? `${API_BASE}/api/v1x/resumes/${resumeId}/education/${educationId}`
        : `${API_BASE}/api/v1x/resumes/${resumeId}/education`;

      const response = await fetch(url, {
        method: educationId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          achievements: formData.achievements.filter(a => a.trim() !== ''),
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to save education');
      }
    } catch (error) {
      console.error('Error saving education:', error);
      alert('Failed to save education');
    } finally {
      setSaving(false);
    }
  };

  const updateAchievement = (index: number, value: string) => {
    const updated = [...formData.achievements];
    updated[index] = value;
    setFormData(prev => ({ ...prev, achievements: updated }));
  };

  const removeAchievement = (index: number) => {
    setFormData(prev => ({
      ...prev,
      achievements: prev.achievements.filter((_, i) => i !== index),
    }));
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {educationId ? 'Edit' : 'Add'} Education
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
            School / University <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.school}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, school: e.target.value })
            }
            placeholder="Stanford University"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Degree <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.degree}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, degree: e.target.value })
              }
              placeholder="Bachelor of Science"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Field of Study <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.field_of_study}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, field_of_study: e.target.value })
              }
              placeholder="Computer Science"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date <span className="text-red-500">*</span>
            </label>
            <Input
              type="month"
              value={formData.start_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, start_date: e.target.value })
              }
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
            <Input
              type="month"
              value={formData.end_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, end_date: e.target.value })
              }
              disabled={formData.is_current}
            />
            <label className="flex items-center mt-2">
              <input
                type="checkbox"
                checked={formData.is_current}
                onChange={(e) =>
                  setFormData({ ...formData, is_current: e.target.checked, end_date: '' })
                }
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Currently studying</span>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">GPA (Optional)</label>
          <Input
            type="text"
            value={formData.gpa}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, gpa: e.target.value })
            }
            placeholder="3.8/4.0"
          />
          <p className="text-xs text-gray-500 mt-1">
            Only include if 3.5+ or required by employer
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Achievements & Honors (Optional)
          </label>
          {formData.achievements.map((achievement, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <Input
                type="text"
                value={achievement}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateAchievement(index, e.target.value)
                }
                placeholder="Dean's List, Summa Cum Laude, etc."
              />
              {formData.achievements.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeAchievement(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() =>
              setFormData(prev => ({ ...prev, achievements: [...prev.achievements, ''] }))
            }
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            + Add Another
          </button>
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
