import { useState } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface WorkExperience {
  id: number;
  company: string;
  position: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description: string;
  responsibilities: string[];
}

interface WorkExperienceSectionProps {
  resumeId: number;
  experiences: WorkExperience[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function WorkExperienceSection({
  resumeId,
  experiences,
  onUpdate,
}: WorkExperienceSectionProps) {
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
    if (!confirm('Are you sure you want to delete this experience?')) return;

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(
        `${API_BASE}/api/v1x/resumes/${resumeId}/work-experience/${id}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting experience:', error);
      alert('Failed to delete experience');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Work Experience</h2>
          <p className="text-gray-600 mt-1">
            List your professional experience in reverse chronological order.
          </p>
        </div>
        <Button onClick={handleAdd} variant="primary">
          + Add Experience
        </Button>
      </div>

      {experiences.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">💼</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No work experience yet</h3>
          <p className="text-gray-600 mb-4">Start by adding your most recent position.</p>
          <Button onClick={handleAdd} variant="primary">
            Add Your First Job
          </Button>
        </Card>
      )}

      {experiences.map((exp) => (
        <Card key={exp.id} className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{exp.position}</h3>
              <p className="text-md text-gray-700 font-medium">{exp.company}</p>
              {exp.location && <p className="text-sm text-gray-500">{exp.location}</p>}
              <p className="text-sm text-gray-500 mt-1">
                {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date || 'Present'}
              </p>
              {exp.responsibilities && exp.responsibilities.length > 0 && (
                <ul className="mt-3 space-y-1">
                  {exp.responsibilities.map((resp, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{resp}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(exp.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(exp.id)}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </Card>
      ))}

      {showForm && (
        <WorkExperienceForm
          resumeId={resumeId}
          experienceId={editingId}
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
interface WorkExperienceFormProps {
  resumeId: number;
  experienceId: number | null;
  onClose: () => void;
  onSave: () => void;
}

function WorkExperienceForm({ resumeId, experienceId, onClose, onSave }: WorkExperienceFormProps) {
  const [formData, setFormData] = useState({
    company: '',
    position: '',
    location: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
    responsibilities: [''],
  });
  const [saving, setSaving] = useState(false);
  const [showAI, setShowAI] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const url = experienceId
        ? `${API_BASE}/api/v1x/resumes/${resumeId}/work-experience/${experienceId}`
        : `${API_BASE}/api/v1x/resumes/${resumeId}/work-experience`;

      const response = await fetch(url, {
        method: experienceId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          responsibilities: formData.responsibilities.filter(r => r.trim() !== ''),
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to save work experience');
      }
    } catch (error) {
      console.error('Error saving experience:', error);
      alert('Failed to save work experience');
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateAI = async () => {
    if (!formData.position || !formData.company) {
      alert('Please enter position and company first');
      return;
    }

    setAiLoading(true);
    setShowAI(true);

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(`${API_BASE}/api/v1x/resume-ai/bullet-points`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          position: formData.position,
          company: formData.company,
          count: 5,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiSuggestions(data.bullet_points || []);
      }
    } catch (error) {
      console.error('Error generating AI bullet points:', error);
      alert('Failed to generate bullet points');
    } finally {
      setAiLoading(false);
    }
  };

  const addBulletPoint = (point: string) => {
    setFormData(prev => ({
      ...prev,
      responsibilities: [...prev.responsibilities.filter(r => r.trim() !== ''), point, ''],
    }));
  };

  const updateResponsibility = (index: number, value: string) => {
    const updated = [...formData.responsibilities];
    updated[index] = value;
    setFormData(prev => ({ ...prev, responsibilities: updated }));
  };

  const removeResponsibility = (index: number) => {
    setFormData(prev => ({
      ...prev,
      responsibilities: prev.responsibilities.filter((_, i) => i !== index),
    }));
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {experienceId ? 'Edit' : 'Add'} Work Experience
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Position <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.position}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, position: e.target.value })
              }
              placeholder="Software Engineer"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.company}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, company: e.target.value })
              }
              placeholder="Google"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
          <Input
            type="text"
            value={formData.location}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, location: e.target.value })
            }
            placeholder="San Francisco, CA"
          />
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
              <span className="text-sm text-gray-700">I currently work here</span>
            </label>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Key Responsibilities & Achievements
            </label>
            <Button
              type="button"
              onClick={handleGenerateAI}
              variant="secondary"
              disabled={aiLoading}
            >
              {aiLoading ? '⏳ Generating...' : '✨ AI Generate'}
            </Button>
          </div>
          {formData.responsibilities.map((resp, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <textarea
                value={resp}
                onChange={(e) => updateResponsibility(index, e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={2}
                placeholder="• Led a team of 5 engineers to build..."
              />
              {formData.responsibilities.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeResponsibility(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => setFormData(prev => ({ ...prev, responsibilities: [...prev.responsibilities, ''] }))}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            + Add Another
          </button>
        </div>

        {showAI && aiSuggestions.length > 0 && (
          <Card className="p-4 bg-purple-50 border-purple-200">
            <h4 className="font-semibold text-gray-900 mb-3">✨ AI-Generated Suggestions:</h4>
            <div className="space-y-2">
              {aiSuggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2 p-3 bg-white rounded-lg hover:shadow-md transition-all border border-gray-200"
                >
                  <p className="flex-1 text-sm text-gray-700">{suggestion}</p>
                  <button
                    type="button"
                    onClick={() => addBulletPoint(suggestion)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium whitespace-nowrap"
                  >
                    + Add
                  </button>
                </div>
              ))}
            </div>
          </Card>
        )}

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
