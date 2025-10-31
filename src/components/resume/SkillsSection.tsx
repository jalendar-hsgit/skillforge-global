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

  const skillsByCategory = {
    technical: skills.filter(s => s.category === 'technical'),
    soft: skills.filter(s => s.category === 'soft'),
    language: skills.filter(s => s.category === 'language'),
    tool: skills.filter(s => s.category === 'tool'),
  };

  const handleDelete = async (id: number) => {
    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(
        `${API_BASE}/api/v1x/resumes/${resumeId}/skills/${id}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting skill:', error);
      alert('Failed to delete skill');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Skills</h2>
          <p className="text-gray-600 mt-1">
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
          }}
        />
      )}

      {/* Pro Tips */}
      {skills.length > 0 && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <h4 className="font-semibold text-gray-900 mb-2">💡 Pro Tips:</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• List 8-12 most relevant skills for the target role</li>
            <li>• Be honest about proficiency levels - they guide interview questions</li>
            <li>• Technical skills are most important for tech roles</li>
            <li>• Include tools/frameworks mentioned in job descriptions</li>
          </ul>
        </Card>
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(`${API_BASE}/api/v1x/resumes/${resumeId}/skills`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to add skill');
      }
    } catch (error) {
      console.error('Error adding skill:', error);
      alert('Failed to add skill');
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
    </Card>
  );
}
