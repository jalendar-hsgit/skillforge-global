import { useState, useEffect } from 'react';
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
  // Backend returns bullet_points; UI historically used responsibilities
  bullet_points?: string[];
  responsibilities?: string[];
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
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

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
      const response = await fetch(
          `/api/session/v1x/work-experience?id=${id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        onUpdate();
        setToast({ type: 'success', message: 'Experience deleted' });
        setTimeout(() => setToast(null), 2000);
      }
    } catch (error) {
      console.error('Error deleting experience:', error);
      setToast({ type: 'error', message: 'Failed to delete experience' });
      setTimeout(() => setToast(null), 2600);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent tracking-tight">Work Experience</h2>
          <p className="text-techGray/80 mt-1">
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

      {experiences.map((exp) => {
        const bullets = (exp.responsibilities && exp.responsibilities.length > 0)
          ? exp.responsibilities
          : (exp.bullet_points || []);
        return (
    <Card key={exp.id} className="p-6 border-white/10 bg-white/5 shadow-lg shadow-black/20">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">{exp.position}</h3>
                <p className="text-sm text-techGray/90 font-semibold">{exp.company}</p>
                {exp.location && <p className="text-xs text-techGray/70 mt-0.5">{exp.location}</p>}
                <p className="text-xs text-techGray/70 mt-1">
                  {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date || 'Present'}
                </p>
                {bullets.length > 0 && (
                  <ul className="mt-3 space-y-1.5">
                    {bullets.map((resp, idx) => (
                      <li key={idx} className="text-sm text-white/90 flex items-start">
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
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-white/20 text-white/90 hover:bg-white/10 transition"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(exp.id)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-400/30 text-red-200 hover:bg-red-500/10 transition"
                >
                  Delete
                </button>
              </div>
            </div>
          </Card>
        );
      })}

      {showForm && (
        <WorkExperienceForm
          resumeId={resumeId}
          experienceId={editingId}
          experience={editingId ? experiences.find(e => e.id === editingId) || null : null}
          onClose={() => {
            setShowForm(false);
            setEditingId(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingId(null);
            onUpdate();
            setToast({ type: 'success', message: 'Experience saved' });
            setTimeout(() => setToast(null), 2000);
          }}
        />
      )}

      {toast && (
        <div className="fixed bottom-6 right-6 z-[60]">
          <div
            className={`min-w-[220px] max-w-sm px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-sm transition-all ${
              toast.type === 'success'
                ? 'bg-green-500/20 border-green-400/40 text-green-100'
                : toast.type === 'error'
                ? 'bg-red-500/20 border-red-400/40 text-red-100'
                : 'bg-blue-500/20 border-blue-400/40 text-blue-100'
            }`}
            role="status"
            aria-live="polite"
          >
            <p className="text-sm font-semibold tracking-wide">{toast.message}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Form Component
interface WorkExperienceFormProps {
  resumeId: number;
  experienceId: number | null;
  experience: WorkExperience | null;
  onClose: () => void;
  onSave: () => void;
}

function WorkExperienceForm({ resumeId, experienceId, experience, onClose, onSave }: WorkExperienceFormProps) {
  const [formData, setFormData] = useState({
    company: experience?.company || '',
    position: experience?.position || '',
    location: experience?.location || '',
    start_date: experience?.start_date || '',
    end_date: experience?.end_date || '',
    is_current: experience?.is_current || false,
    description: experience?.description || '',
    responsibilities: (
      (experience?.responsibilities && experience?.responsibilities.length ? experience.responsibilities : experience?.bullet_points) || ['']
    ) as string[],
  });
  const [saving, setSaving] = useState(false);
  // Keep form in sync when user selects another item to edit
  useEffect(() => {
    if (experienceId && experience) {
      setFormData({
        company: experience.company || '',
        position: experience.position || '',
        location: experience.location || '',
        start_date: experience.start_date || '',
        end_date: experience.end_date || '',
        is_current: !!experience.is_current,
        description: experience.description || '',
        responsibilities: (
          (experience.responsibilities && experience.responsibilities.length ? experience.responsibilities : experience.bullet_points) || ['']
        ) as string[],
      });
    } else if (!experienceId) {
      setFormData({
        company: '',
        position: '',
        location: '',
        start_date: '',
        end_date: '',
        is_current: false,
        description: '',
        responsibilities: [''],
      });
    }
  }, [experienceId, experience]);
  const [showAI, setShowAI] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const url = experienceId
          ? `/api/session/v1x/work-experience?id=${experienceId}`
          : `/api/session/v1x/work-experience?resumeId=${resumeId}`;

      const response = await fetch(url, {
        method: experienceId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...formData,
          // Map UI responsibilities -> backend bullet_points
          bullet_points: formData.responsibilities.filter(r => r.trim() !== ''),
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        setToast({ type: 'error', message: 'Failed to save work experience' });
        setTimeout(() => setToast(null), 2600);
      }
    } catch (error) {
      console.error('Error saving experience:', error);
      setToast({ type: 'error', message: 'Failed to save work experience' });
      setTimeout(() => setToast(null), 2600);
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateAI = async () => {
    if (!formData.position || !formData.company) {
      setToast({ type: 'info', message: 'Enter position and company first' });
      setTimeout(() => setToast(null), 2200);
      return;
    }

    setAiLoading(true);
    setShowAI(true);

    try {
      const response = await fetch(`/api/session/resume-ai/bullets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          job_title: formData.position,
          company: formData.company,
          description: formData.description || '',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiSuggestions((data.bullets || data.bullet_points || []) as string[]);
        setToast({ type: 'success', message: 'AI suggestions ready' });
        setTimeout(() => setToast(null), 2000);
      }
    } catch (error) {
      console.error('Error generating AI bullet points:', error);
      setToast({ type: 'error', message: 'Failed to generate bullet points' });
      setTimeout(() => setToast(null), 2600);
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
    <Card className="p-0 overflow-hidden">
      <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-forgePurple/20 via-neuralBlue/10 to-forgePurple/20 flex items-center justify-between">
        <h3 className="text-sm font-black tracking-wider text-white/90">
          {experienceId ? 'Edit' : 'Add'} Work Experience
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="px-2 py-1 rounded-lg text-white/80 hover:bg-white/10 transition"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4 p-6">

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
