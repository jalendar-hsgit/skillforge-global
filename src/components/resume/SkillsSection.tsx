import { useState } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface Skill {
  id: number;
  name: string;
  category: 'technical' | 'soft' | 'language' | 'tool';
  proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}

interface SkillsSectionProps {
  resumeId: number;
  skills: Skill[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

const CATEGORY_LABELS = {
  technical: '⚡ Technical Skills',
  soft: '🤝 Soft Skills',
  language: '🌐 Languages',
  tool: '🛠️ Tools & Technologies',
};

const PROFICIENCY_LABELS = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  expert: 'Expert',
};

const PROFICIENCY_COLORS = {
  beginner: 'bg-gray-200 text-gray-700',
  intermediate: 'bg-blue-200 text-blue-700',
  advanced: 'bg-green-200 text-green-700',
  expert: 'bg-purple-200 text-purple-700',
};

export default function SkillsSection({
  resumeId,
  skills,
  onUpdate,
}: SkillsSectionProps) {
  const [showForm, setShowForm] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const skillsByCategory = {
    technical: skills.filter(s => s.category === 'technical'),
    soft: skills.filter(s => s.category === 'soft'),
    language: skills.filter(s => s.category === 'language'),
    tool: skills.filter(s => s.category === 'tool'),
  };

  const handleDelete = async (id: number) => {
    try {
      const response = await fetch(
        `/api/session/v1x/skills?id=${id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        onUpdate();
        setToast({ type: 'success', message: 'Skill removed' });
        setTimeout(() => setToast(null), 2000);
      } else {
        const text = await response.text();
        console.error('Failed to delete skill:', text);
        setToast({ type: 'error', message: 'Failed to delete skill' });
        setTimeout(() => setToast(null), 2600);
      }
    } catch (error) {
      console.error('Error deleting skill:', error);
      setToast({ type: 'error', message: 'Failed to delete skill' });
      setTimeout(() => setToast(null), 2600);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent tracking-tight">Skills</h2>
          <p className="text-techGray/80 mt-1">
            Showcase your technical and soft skills with proficiency levels.
          </p>
        </div>
        <Button onClick={() => setShowForm(true)} variant="primary">
          + Add Skill
        </Button>
      </div>

      {skills.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">⚡</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No skills yet</h3>
          <p className="text-gray-600 mb-4">
            Add your technical skills, languages, and tools you're proficient in.
          </p>
          <Button onClick={() => setShowForm(true)} variant="primary">
            Add Your First Skill
          </Button>
        </Card>
      )}

      {Object.entries(skillsByCategory).map(([category, categorySkills]) => {
        if (categorySkills.length === 0) return null;
        return (
          <div key={category}>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              {CATEGORY_LABELS[category as keyof typeof CATEGORY_LABELS]}
            </h3>
            <Card className="p-4">
              <div className="flex flex-wrap gap-2">
                {categorySkills.map((skill) => (
                  <div
                    key={skill.id}
                    className="group flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full hover:shadow-md transition-all"
                  >
                    <span className="font-medium text-gray-900">{skill.name}</span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        PROFICIENCY_COLORS[skill.proficiency]
                      }`}
                    >
                      {PROFICIENCY_LABELS[skill.proficiency]}
                    </span>
                    <button
                      onClick={() => handleDelete(skill.id)}
                      className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        );
      })}

      {showForm && (
        <SkillForm
          resumeId={resumeId}
          onClose={() => setShowForm(false)}
          onSave={() => {
            setShowForm(false);
            onUpdate();
            setToast({ type: 'success', message: 'Skill added' });
            setTimeout(() => setToast(null), 2000);
          }}
        />
      )}

      {/* Pro Tips (screen only) */}
      {skills.length > 0 && (
        <Card className="p-4 bg-blue-50 border-blue-200 print:hidden">
          <h4 className="font-semibold text-gray-900 mb-2">💡 Pro Tips:</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• List 8-12 most relevant skills for the target role</li>
            <li>• Be honest about proficiency levels - they guide interview questions</li>
            <li>• Technical skills are most important for tech roles</li>
            <li>• Include tools/frameworks mentioned in job descriptions</li>
          </ul>
        </Card>
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
interface SkillFormProps {
  resumeId: number;
  onClose: () => void;
  onSave: () => void;
}

function SkillForm({ resumeId, onClose, onSave }: SkillFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    category: 'technical' as 'technical' | 'soft' | 'language' | 'tool',
    proficiency: 'intermediate' as 'beginner' | 'intermediate' | 'advanced' | 'expert',
  });
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await fetch(`/api/session/v1x/skills?resumeId=${resumeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        onSave();
      } else {
        setToast({ type: 'error', message: 'Failed to add skill' });
        setTimeout(() => setToast(null), 2600);
      }
    } catch (error) {
      console.error('Error adding skill:', error);
      setToast({ type: 'error', message: 'Failed to add skill' });
      setTimeout(() => setToast(null), 2600);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">Add Skill</h3>
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
            Skill Name <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, name: e.target.value })
            }
            placeholder="e.g., JavaScript, Project Management, Spanish"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.category}
            onChange={(e) =>
              setFormData({
                ...formData,
                category: e.target.value as 'technical' | 'soft' | 'language' | 'tool',
              })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          >
            <option value="technical">⚡ Technical Skills</option>
            <option value="tool">🛠️ Tools & Technologies</option>
            <option value="soft">🤝 Soft Skills</option>
            <option value="language">🌐 Languages</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Proficiency Level <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(PROFICIENCY_LABELS).map(([key, label]) => (
              <button
                key={key}
                type="button"
                onClick={() =>
                  setFormData({
                    ...formData,
                    proficiency: key as 'beginner' | 'intermediate' | 'advanced' | 'expert',
                  })
                }
                className={`px-4 py-3 rounded-lg border-2 font-medium transition-all ${
                  formData.proficiency === key
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="submit" variant="primary" disabled={saving}>
            {saving ? 'Adding...' : 'Add Skill'}
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
