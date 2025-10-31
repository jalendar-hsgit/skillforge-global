import React, { useState, useEffect } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface Project {
  id: number;
  name: string;
  description: string;
  tech_stack: string[];
  github_url?: string;
  live_url?: string;
  start_date?: string;
  end_date?: string;
}

interface ProjectsSectionProps {
  resumeId: number;
  projects: Project[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

const PROJECT_TEMPLATES = [
  {
    name: 'Task Management System',
    description: 'Built a full-stack task management application with real-time collaboration features, drag-and-drop interface, and team workspace management.',
    tech_stack: ['React', 'Node.js', 'MongoDB', 'Socket.IO', 'Tailwind CSS'],
  },
  {
    name: 'E-Commerce Platform',
    description: 'Developed a scalable e-commerce platform with product catalog, shopping cart, payment integration, order tracking, and admin dashboard.',
    tech_stack: ['Next.js', 'TypeScript', 'PostgreSQL', 'Stripe', 'Redis'],
  },
  {
    name: 'AI-Powered Chat Application',
    description: 'Created an intelligent chatbot application using natural language processing for customer support automation with sentiment analysis and multi-language support.',
    tech_stack: ['Python', 'FastAPI', 'OpenAI API', 'React', 'Docker'],
  },
  {
    name: 'Microservices Architecture',
    description: 'Designed and implemented a microservices-based architecture for a high-traffic application with API gateway, service discovery, and distributed tracing.',
    tech_stack: ['Java', 'Spring Boot', 'Kubernetes', 'Kafka', 'Prometheus'],
  },
  {
    name: 'Data Analytics Dashboard',
    description: 'Built an interactive analytics dashboard with real-time data visualization, custom reports, and automated insights using machine learning algorithms.',
    tech_stack: ['Python', 'Pandas', 'Plotly', 'Dash', 'PostgreSQL'],
  },
  {
    name: 'SaaS Platform',
    description: 'Developed a multi-tenant SaaS platform with subscription management, role-based access control, and comprehensive API for third-party integrations.',
    tech_stack: ['Vue.js', 'Django', 'PostgreSQL', 'AWS', 'Celery'],
  },
];

export default function ProjectsSection({
  resumeId,
  projects,
  onUpdate,
}: ProjectsSectionProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<typeof PROJECT_TEMPLATES[0] | null>(null);

  const handleAdd = () => {
    setEditingId(null);
    setShowForm(true);
  };

  const handleEdit = (id: number) => {
    setEditingId(id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(
        `${API_BASE}/api/v1x/resumes/${resumeId}/projects/${id}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      alert('Failed to delete project');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
          <p className="text-gray-600 mt-1">
            Showcase your personal or professional projects that demonstrate your skills.
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowTemplates(true)} variant="secondary">
            ✨ Use Template
          </Button>
          <Button onClick={handleAdd} variant="primary">
            + Add Project
          </Button>
        </div>
      </div>

      {projects.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🚀</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-600 mb-4">
            Add projects to demonstrate your practical skills and achievements.
          </p>
          <div className="flex gap-3 justify-center">
            <Button onClick={handleAdd} variant="primary">
              Add Project
            </Button>
            <Button onClick={() => setShowTemplates(true)} variant="secondary">
              Browse Templates
            </Button>
          </div>
        </Card>
      )}

      {projects.map((project) => (
        <Card key={project.id} className="p-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <h3 className="text-lg font-bold text-gray-900">{project.name}</h3>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleEdit(project.id)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(project.id)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
              {(project.start_date || project.end_date) && (
                <p className="text-sm text-gray-500 mt-1">
                  {project.start_date} {project.end_date && `- ${project.end_date}`}
                </p>
              )}
              <p className="text-sm text-gray-700 mt-2">{project.description}</p>
              {project.tech_stack && project.tech_stack.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {project.tech_stack.map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              {(project.github_url || project.live_url) && (
                <div className="flex gap-4 mt-3">
                  {project.github_url && (
                    <a
                      href={project.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      🔗 GitHub
                    </a>
                  )}
                  {project.live_url && (
                    <a
                      href={project.live_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      🌐 Live Demo
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        </Card>
      ))}

      {showForm && (
        <ProjectForm
          resumeId={resumeId}
          projectId={editingId}
          template={selectedTemplate || undefined}
          onClose={() => {
            setShowForm(false);
            setEditingId(null);
            setSelectedTemplate(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingId(null);
            setSelectedTemplate(null);
            onUpdate();
          }}
        />
      )}

      {showTemplates && (
        <ProjectTemplatesModal
          onSelect={(template) => {
            setShowTemplates(false);
            setSelectedTemplate(template);
            setShowForm(true);
          }}
          onClose={() => setShowTemplates(false)}
        />
      )}

      {/* Pro Tips */}
      {projects.length > 0 && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <h4 className="font-semibold text-gray-900 mb-2">💡 Pro Tips:</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Focus on 2-4 most impressive and relevant projects</li>
            <li>• Include metrics (users, performance improvements, etc.)</li>
            <li>• Link to GitHub repo or live demo when possible</li>
            <li>• Highlight technologies matching the job description</li>
          </ul>
        </Card>
      )}
    </div>
  );
}

// Form Component
interface ProjectFormProps {
  resumeId: number;
  projectId: number | null;
  template?: typeof PROJECT_TEMPLATES[0];
  onClose: () => void;
  onSave: () => void;
}

function ProjectForm({ resumeId, projectId, template, onClose, onSave }: ProjectFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tech_stack: [''],
    github_url: '',
    live_url: '',
    start_date: '',
    end_date: '',
  });
  const [saving, setSaving] = useState(false);

  // Prefill when a template is provided
  React.useEffect(() => {
    if (template) {
      setFormData(prev => ({
        ...prev,
        name: template.name,
        description: template.description,
        tech_stack: [...template.tech_stack],
      }))
    }
  }, [template])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const url = projectId
        ? `${API_BASE}/api/v1x/resumes/${resumeId}/projects/${projectId}`
        : `${API_BASE}/api/v1x/resumes/${resumeId}/projects`;

      const response = await fetch(url, {
        method: projectId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          tech_stack: formData.tech_stack.filter(t => t.trim() !== ''),
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to save project');
      }
    } catch (error) {
      console.error('Error saving project:', error);
      alert('Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const updateTech = (index: number, value: string) => {
    const updated = [...formData.tech_stack];
    updated[index] = value;
    setFormData(prev => ({ ...prev, tech_stack: updated }));
  };

  const removeTech = (index: number) => {
    setFormData(prev => ({
      ...prev,
      tech_stack: prev.tech_stack.filter((_, i) => i !== index),
    }));
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {projectId ? 'Edit' : 'Add'} Project
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
            Project Name <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, name: e.target.value })
            }
            placeholder="Task Management System"
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
            rows={4}
            placeholder="Describe what you built, technologies used, and your role..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tech Stack <span className="text-red-500">*</span>
          </label>
          {formData.tech_stack.map((tech, index) => (
            <div key={index} className="flex gap-2 mb-2">
              <Input
                type="text"
                value={tech}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateTech(index, e.target.value)
                }
                placeholder="React, Node.js, MongoDB..."
              />
              {formData.tech_stack.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeTech(index)}
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
              setFormData(prev => ({ ...prev, tech_stack: [...prev.tech_stack, ''] }))
            }
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            + Add Technology
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">GitHub URL</label>
            <Input
              type="url"
              value={formData.github_url}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, github_url: e.target.value })
              }
              placeholder="https://github.com/..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Live Demo URL</label>
            <Input
              type="url"
              value={formData.live_url}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, live_url: e.target.value })
              }
              placeholder="https://..."
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
            <Input
              type="month"
              value={formData.start_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, start_date: e.target.value })
              }
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
            />
          </div>
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

// Templates Modal
interface ProjectTemplatesModalProps {
  onSelect: (template: typeof PROJECT_TEMPLATES[0]) => void;
  onClose: () => void;
}

function ProjectTemplatesModal({ onSelect, onClose }: ProjectTemplatesModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Project Templates</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <p className="text-gray-600 mb-6">
          Choose a template to get started. You can customize it after adding.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PROJECT_TEMPLATES.map((template, idx) => (
            <Card
              key={idx}
              className="p-4 hover:shadow-lg transition-all cursor-pointer border-2 border-transparent hover:border-blue-500"
              onClick={() => onSelect(template)}
            >
              <h3 className="font-bold text-gray-900 mb-2">{template.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
              <div className="flex flex-wrap gap-2">
                {template.tech_stack.slice(0, 3).map((tech, techIdx) => (
                  <span
                    key={techIdx}
                    className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium"
                  >
                    {tech}
                  </span>
                ))}
                {template.tech_stack.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                    +{template.tech_stack.length - 3} more
                  </span>
                )}
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  );
}
