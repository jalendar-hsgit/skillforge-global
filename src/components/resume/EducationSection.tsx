import { useState, useEffect } from 'react';
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

export default function EducationSection({
  resumeId,
  education,
  onUpdate,
}: EducationSectionProps) {
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
    if (!confirm('Are you sure you want to delete this education?')) return;

    try {
      const response = await fetch(
        `/api/session/v1x/education?id=${id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        onUpdate();
        setToast({ type: 'success', message: 'Education deleted' });
        setTimeout(() => setToast(null), 2000);
      }
    } catch (error) {
      console.error('Error deleting education:', error);
      setToast({ type: 'error', message: 'Failed to delete education' });
      setTimeout(() => setToast(null), 2600);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent tracking-tight">Education</h2>
          <p className="text-techGray/80 mt-1">
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
        <Card key={edu.id} className="p-6 border-white/10 bg-white/5 shadow-lg shadow-black/20">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight">
                {edu.degree} in {edu.field_of_study}
              </h3>
              <p className="text-sm text-techGray/90 font-semibold">{edu.school}</p>
              <p className="text-xs text-techGray/70 mt-1">
                {edu.start_date} - {edu.is_current ? 'Present' : edu.end_date || 'Present'}
              </p>
              {edu.gpa && (
                <p className="text-xs text-techGray/70 mt-1">GPA: {edu.gpa}</p>
              )}
              {edu.achievements && edu.achievements.length > 0 && (
                <ul className="mt-3 space-y-1.5">
                  {edu.achievements.map((achievement, idx) => (
                    <li key={idx} className="text-sm text-white/90 flex items-start">
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
                className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-white/20 text-white/90 hover:bg-white/10 transition"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(edu.id)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-400/30 text-red-200 hover:bg-red-500/10 transition"
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
          educationItem={editingId ? education.find(e => e.id === editingId) || null : null}
          onClose={() => {
            setShowForm(false);
            setEditingId(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingId(null);
            onUpdate();
            setToast({ type: 'success', message: 'Education saved' });
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
interface EducationFormProps {
  resumeId: number;
  educationId: number | null;
  educationItem: Education | null;
  onClose: () => void;
  onSave: () => void;
}

function EducationForm({ resumeId, educationId, educationItem, onClose, onSave }: EducationFormProps) {
  const [formData, setFormData] = useState({
    school: educationItem?.school || '',
    degree: educationItem?.degree || '',
    field_of_study: educationItem?.field_of_study || '',
    start_date: educationItem?.start_date || '',
    end_date: educationItem?.end_date || '',
    is_current: educationItem?.is_current || false,
    gpa: educationItem?.gpa || '',
    achievements: educationItem?.achievements && educationItem.achievements.length ? educationItem.achievements : [''],
  });
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // Prefill form when editing and keep in sync
  useEffect(() => {
    if (educationId && educationItem) {
      setFormData({
        school: educationItem.school || '',
        degree: educationItem.degree || '',
        field_of_study: educationItem.field_of_study || '',
        start_date: educationItem.start_date || '',
        end_date: educationItem.end_date || '',
        is_current: !!educationItem.is_current,
        gpa: educationItem.gpa || '',
        achievements: educationItem.achievements && educationItem.achievements.length ? educationItem.achievements : [''],
      });
    } else if (!educationId) {
      setFormData({
        school: '',
        degree: '',
        field_of_study: '',
        start_date: '',
        end_date: '',
        is_current: false,
        gpa: '',
        achievements: [''],
      });
    }
  }, [educationId, educationItem]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const url = educationId
        ? `/api/session/v1x/education?id=${educationId}`
        : `/api/session/v1x/education?resumeId=${resumeId}`;

      const response = await fetch(url, {
        method: educationId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          institution: formData.school,
          degree: formData.degree,
          field_of_study: formData.field_of_study,
          start_date: formData.start_date,
          end_date: formData.end_date,
          is_current: formData.is_current,
          gpa: formData.gpa,
          achievements: formData.achievements.filter(a => a.trim() !== ''),
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        setToast({ type: 'error', message: 'Failed to save education' });
        setTimeout(() => setToast(null), 2600);
      }
    } catch (error) {
      console.error('Error saving education:', error);
      setToast({ type: 'error', message: 'Failed to save education' });
      setTimeout(() => setToast(null), 2600);
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
    <Card className="p-0 overflow-hidden">
      <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-forgePurple/20 via-neuralBlue/10 to-forgePurple/20 flex items-center justify-between">
        <h3 className="text-sm font-black tracking-wider text-white/90">
          {educationId ? 'Edit' : 'Add'} Education
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
    </Card>
  );
}
