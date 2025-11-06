import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { 
  Sparkles, Save, Download, Eye, Layout as LayoutIcon, 
  GripVertical, Plus, Trash2, ChevronDown, ChevronUp,
  Wand2, FileText, AlertCircle, Check
} from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface Resume {
  id: number;
  title: string;
  template: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  professional_summary?: string;
  work_experiences: any[];
  education: any[];
  skills: any[];
  projects: any[];
  certificates: any[];
  achievements: any[];
  created_at: string;
  updated_at: string;
}

interface Section {
  id: string;
  title: string;
  icon: any;
  enabled: boolean;
  order: number;
}

interface ResumeEditorProps {
  resumeId: number;
}

const TEMPLATES = [
  { id: 'professional', name: 'Professional', preview: '/templates/professional.png' },
  { id: 'modern', name: 'Modern', preview: '/templates/modern.png' },
  { id: 'creative', name: 'Creative', preview: '/templates/creative.png' },
  { id: 'minimal', name: 'Minimal', preview: '/templates/minimal.png' },
];

export default function EnhancedResumeEditor({ resumeId }: ResumeEditorProps) {
  const router = useRouter();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>('header');
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [sections, setSections] = useState<Section[]>([
    { id: 'header', title: 'Contact Info', icon: FileText, enabled: true, order: 0 },
    { id: 'summary', title: 'Professional Summary', icon: Sparkles, enabled: true, order: 1 },
    { id: 'experience', title: 'Work Experience', icon: FileText, enabled: true, order: 2 },
    { id: 'education', title: 'Education', icon: FileText, enabled: true, order: 3 },
    { id: 'skills', title: 'Skills', icon: FileText, enabled: true, order: 4 },
    { id: 'projects', title: 'Projects', icon: FileText, enabled: true, order: 5 },
    { id: 'certificates', title: 'Certificates', icon: FileText, enabled: false, order: 6 },
    { id: 'achievements', title: 'Achievements', icon: FileText, enabled: false, order: 7 },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    loadResume();
  }, [resumeId]);

  const loadResume = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/session/resumes?id=${resumeId}`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setResume(data);
        fetchATSScore();
      } else if (response.status === 401) {
        router.push('/login?redirect=' + encodeURIComponent(`/resumes/${resumeId}`));
        return;
      }
    } catch (error) {
      console.error('Error loading resume:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchATSScore = async () => {
    try {
      const response = await fetch(`/api/session/resume-ai/ats-score/${resumeId}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setAtsScore(data.score || 0);
      }
    } catch (error) {
      console.error('Error fetching ATS score:', error);
    }
  };

  const saveResume = useCallback(async (data: Partial<Resume>) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(async () => {
      try {
        setSaving(true);
        const response = await fetch(`/api/session/resumes?id=${resumeId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(data),
        });

        if (response.ok) {
          setLastSaved(new Date());
          fetchATSScore(); // Refresh ATS score after save
        }
      } catch (error) {
        console.error('Error saving resume:', error);
      } finally {
        setSaving(false);
      }
    }, 2000); // 2 second debounce
  }, [resumeId]);

  const updateResume = (updates: Partial<Resume>) => {
    setResume(prev => {
      if (!prev) return prev;
      const updated = { ...prev, ...updates };
      saveResume(updates);
      return updated;
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setSections((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  if (loading || !resume) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple mx-auto mb-4"></div>
            <p className="text-techGray">Loading resume...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout showFooter={false} maxWidth="full">
      {/* Top Action Bar */}
      <div className="bg-gradient-to-r from-deepTech via-[#1a1625] to-deepTech border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-[2000px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-techGray hover:text-white transition-colors"
              >
                ← Dashboard
              </button>
              <div>
                <input
                  type="text"
                  value={resume.title}
                  onChange={(e) => updateResume({ title: e.target.value })}
                  className="text-xl font-semibold text-white bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-forgePurple"
                  placeholder="Untitled Resume"
                  data-testid="input-title"
                />
                <p className="text-sm text-techGray mt-1" data-testid="status-save">
                  {saving ? (
                    <span className="flex items-center gap-2">
                      <Save className="w-3 h-3 animate-pulse" /> Saving...
                    </span>
                  ) : lastSaved ? (
                    <span className="flex items-center gap-2">
                      <Check className="w-3 h-3 text-green-400" /> Last saved {lastSaved.toLocaleTimeString()}
                    </span>
                  ) : (
                    'Not saved'
                  )}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              {/* ATS Score Badge */}
              {atsScore !== null && (
                <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
                  <span className="text-sm text-techGray">ATS Score:</span>
                  <span className={`text-lg font-bold ${
                    atsScore >= 80 ? 'text-green-400' : 
                    atsScore >= 60 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {atsScore}/100
                  </span>
                </div>
              )}

              <button
                onClick={() => setShowAIPanel(!showAIPanel)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 transition-all font-semibold"
                data-testid="btn-ai-panel"
              >
                <Wand2 className="w-4 h-4" />
                AI Assistant
              </button>

              <button
                onClick={() => setShowTemplates(!showTemplates)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
              >
                <LayoutIcon className="w-4 h-4" />
                Templates
              </button>

              <button
                onClick={() => window.open(`/resumes/${resumeId}/preview`, '_blank')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
                data-testid="btn-full-preview"
              >
                <Eye className="w-4 h-4" />
                Preview
              </button>

              <button
                onClick={async () => {
                  setExporting(true);
                  setTimeout(() => setExporting(false), 2000);
                }}
                disabled={exporting}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 hover:opacity-90 transition-all font-semibold disabled:opacity-50"
                data-testid="btn-export-pdf"
              >
                <Download className="w-4 h-4" />
                {exporting ? 'Exporting…' : 'Export PDF'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Editor Layout */}
      <div className="flex h-[calc(100vh-120px)] bg-gradient-to-br from-deepTech via-[#1a1625] to-deepTech">
        {/* Left: Drag-and-Drop Section Manager */}
        <div className="w-80 border-r border-white/10 overflow-y-auto bg-black/20 backdrop-blur-sm">
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Resume Sections</h3>
              <button className="text-xs text-forgePurple hover:text-neuralBlue transition-colors">
                Reset Order
              </button>
            </div>

            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={sections.map(s => s.id)} strategy={verticalListSortingStrategy}>
                {sections.map((section) => (
                  <SortableSection
                    key={section.id}
                    section={section}
                    isActive={activeSection === section.id}
                    onClick={() => setActiveSection(section.id)}
                    onToggle={() => {
                      setSections(prev =>
                        prev.map(s => s.id === section.id ? { ...s, enabled: !s.enabled } : s)
                      );
                    }}
                  />
                ))}
              </SortableContext>
            </DndContext>

            <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10">
              <h4 className="text-sm font-semibold text-white mb-2">💡 Pro Tip</h4>
              <p className="text-xs text-techGray">
                Drag sections to reorder them. Disable sections you don't need.
              </p>
            </div>
          </div>
        </div>

        {/* Center: Editor Form */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            <EditorContent
              section={activeSection}
              resume={resume}
              updateResume={updateResume}
              resumeId={resumeId}
              onReload={loadResume}
            />
          </div>
        </div>

        {/* Right: AI Assistant Panel (Collapsible) */}
        {showAIPanel && (
          <AIAssistantPanel
            resume={resume}
            resumeId={resumeId}
            onClose={() => setShowAIPanel(false)}
            onApply={(field: string, value: any) => updateResume({ [field]: value })}
          />
        )}

        {/* Right: Live Preview (when AI panel closed) */}
        {!showAIPanel && (
          <div className="w-96 border-l border-white/10 overflow-y-auto bg-black/20 backdrop-blur-sm p-6">
            <h3 className="text-lg font-semibold text-white mb-4" data-testid="editor-live-preview">Live Preview</h3>
            <div className="bg-white rounded-xl shadow-2xl p-8 text-gray-900 text-sm space-y-4 transform scale-75 origin-top">
              <LivePreview resume={resume} />
            </div>
          </div>
        )}
      </div>

      {/* Template Selector Modal */}
      {showTemplates && (
        <TemplateModal
          currentTemplate={resume.template}
          onSelect={(template: string) => {
            updateResume({ template });
            setShowTemplates(false);
          }}
          onClose={() => setShowTemplates(false)}
        />
      )}
    </Layout>
  );
}

// Sortable Section Component
function SortableSection({ section, isActive, onClick, onToggle }: any) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: section.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
        isActive
          ? 'bg-gradient-to-r from-forgePurple/20 to-neuralBlue/20 border-forgePurple'
          : section.enabled
          ? 'bg-white/5 border-white/10 hover:bg-white/10'
          : 'bg-white/5 border-white/5 opacity-50'
      }`}
    >
      <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing text-techGray hover:text-white">
        <GripVertical className="w-5 h-5" />
      </div>
      <button onClick={onClick} className="flex-1 text-left">
        <span className={`text-sm font-medium ${isActive ? 'text-white' : 'text-techGray'}`}>
          {section.title}
        </span>
      </button>
      <input
        type="checkbox"
        checked={section.enabled}
        onChange={onToggle}
        className="w-4 h-4 rounded border-white/20 bg-white/5 text-forgePurple focus:ring-forgePurple"
      />
    </div>
  );
}

// Editor Content Switcher
function EditorContent({ section, resume, updateResume, resumeId, onReload }: any) {
  switch (section) {
    case 'header':
      return <HeaderSection resume={resume} updateResume={updateResume} />;
    case 'summary':
      return <SummarySection resume={resume} updateResume={updateResume} resumeId={resumeId} />;
    case 'experience':
      return <ExperienceSection resumeId={resumeId} experiences={resume.work_experiences} onReload={onReload} />;
    case 'education':
      return <EducationSection resumeId={resumeId} education={resume.education} onReload={onReload} />;
    case 'skills':
      return <SkillsSection resumeId={resumeId} skills={resume.skills} onReload={onReload} />;
    case 'projects':
      return <ProjectsSection resumeId={resumeId} projects={resume.projects} onReload={onReload} />;
    case 'certificates':
      return <CertificatesSection resumeId={resumeId} certificates={resume.certificates} onReload={onReload} />;
    case 'achievements':
      return <AchievementsSection resumeId={resumeId} achievements={resume.achievements} onReload={onReload} />;
    default:
      return <div className="text-techGray">Select a section</div>;
  }
}

// Header Section
function HeaderSection({ resume, updateResume }: any) {
  return (
    <div className="space-y-6 bg-white/5 rounded-2xl p-8 border border-white/10">
      <h2 className="text-2xl font-bold text-white flex items-center gap-3">
        <FileText className="w-6 h-6 text-forgePurple" />
        Contact Information
      </h2>
      <div className="grid md:grid-cols-2 gap-4">
        <InputField label="Full Name" value={resume.full_name} onChange={(v: string) => updateResume({ full_name: v })} placeholder="John Doe" />
        <InputField label="Email" value={resume.email} onChange={(v: string) => updateResume({ email: v })} placeholder="john@example.com" type="email" />
        <InputField label="Phone" value={resume.phone} onChange={(v: string) => updateResume({ phone: v })} placeholder="+1 (555) 123-4567" />
        <InputField label="Location" value={resume.location} onChange={(v: string) => updateResume({ location: v })} placeholder="San Francisco, CA" />
        <InputField label="LinkedIn" value={resume.linkedin} onChange={(v: string) => updateResume({ linkedin: v })} placeholder="linkedin.com/in/johndoe" />
        <InputField label="GitHub" value={resume.github} onChange={(v: string) => updateResume({ github: v })} placeholder="github.com/johndoe" />
      </div>
    </div>
  );
}

// Summary Section
function SummarySection({ resume, updateResume, resumeId }: any) {
  const [generating, setGenerating] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const generateSummary = async () => {
    setGenerating(true);
    try {
      const response = await fetch(`/api/session/resume-ai/professional-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title: resume.title || 'Professional', years_of_experience: 3 }),
      });
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.summaries || []);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 bg-white/5 rounded-2xl p-8 border border-white/10">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <Sparkles className="w-6 h-6 text-forgePurple" />
          Professional Summary
        </h2>
        <button
          onClick={generateSummary}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 transition-all font-semibold text-sm disabled:opacity-50"
          data-testid="btn-ai-generate"
        >
          <Wand2 className="w-4 h-4" />
          {generating ? 'Generating...' : 'AI Generate'}
        </button>
      </div>
      <p className="text-sm text-techGray">
        Write a compelling 2-3 sentence summary highlighting your key strengths and career goals.
      </p>
      <textarea
        value={resume.professional_summary || ''}
        onChange={(e) => updateResume({ professional_summary: e.target.value })}
        rows={6}
        className="w-full px-4 py-3 bg-black/30 border border-white/10 rounded-lg text-white placeholder:text-techGray focus:outline-none focus:ring-2 focus:ring-forgePurple"
        placeholder="e.g., Results-driven Software Engineer with 5+ years building scalable applications..."
      />
      {suggestions.length > 0 && (
        <div className="space-y-2" data-testid="ai-suggestions">
          <h4 className="text-sm font-semibold text-white">AI Suggestions:</h4>
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => {
                updateResume({ professional_summary: s });
                setSuggestions([]);
              }}
              className="w-full text-left p-4 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-all"
            >
              <p className="text-sm text-techGray">{s}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Placeholder sections (replace with full implementations)
function ExperienceSection({ resumeId, experiences, onReload }: any) {
  return <div className="text-white">Work Experience Editor (use existing component)</div>;
}

function EducationSection({ resumeId, education, onReload }: any) {
  return <div className="text-white">Education Editor</div>;
}

function SkillsSection({ resumeId, skills, onReload }: any) {
  return <div className="text-white">Skills Editor</div>;
}

function ProjectsSection({ resumeId, projects, onReload }: any) {
  return <div className="text-white">Projects Editor</div>;
}

function CertificatesSection({ resumeId, certificates, onReload }: any) {
  return <div className="text-white">Certificates Editor</div>;
}

function AchievementsSection({ resumeId, achievements, onReload }: any) {
  return <div className="text-white">Achievements Editor</div>;
}

// Input Field Component
function InputField({ label, value, onChange, placeholder, type = 'text' }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-white mb-2">{label}</label>
      <input
        type={type}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-2 bg-black/30 border border-white/10 rounded-lg text-white placeholder:text-techGray focus:outline-none focus:ring-2 focus:ring-forgePurple"
      />
    </div>
  );
}

// AI Assistant Panel
function AIAssistantPanel({ resume, resumeId, onClose, onApply }: any) {
  const [activeAI, setActiveAI] = useState<'bullets' | 'summary' | 'keywords' | 'projects'>('bullets');

  return (
    <div className="w-96 border-l border-white/10 overflow-y-auto bg-black/30 backdrop-blur-sm">
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-forgePurple" />
            AI Assistant
          </h3>
          <button onClick={onClose} className="text-techGray hover:text-white">✕</button>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {['bullets', 'summary', 'keywords', 'projects'].map((ai) => (
            <button
              key={ai}
              onClick={() => setActiveAI(ai as any)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                activeAI === ai
                  ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white'
                  : 'bg-white/5 text-techGray hover:bg-white/10'
              }`}
            >
              {ai.charAt(0).toUpperCase() + ai.slice(1)}
            </button>
          ))}
        </div>

        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
          <p className="text-sm text-techGray">
            {activeAI === 'bullets' && 'Generate compelling bullet points for your experience.'}
            {activeAI === 'summary' && 'Create a professional summary tailored to your career.'}
            {activeAI === 'keywords' && 'Optimize your resume with ATS-friendly keywords.'}
            {activeAI === 'projects' && 'Get project ideas to strengthen your portfolio.'}
          </p>
          <button className="mt-4 w-full px-4 py-2 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue hover:opacity-90 transition-all font-semibold text-sm">
            Generate
          </button>
        </div>
      </div>
    </div>
  );
}

// Live Preview
function LivePreview({ resume }: { resume: Resume }) {
  return (
    <div className="space-y-4">
      <div className="text-center border-b pb-4">
        <h1 className="text-2xl font-bold">{resume.full_name || 'Your Name'}</h1>
        <p className="text-sm text-gray-600 mt-1">{resume.email} | {resume.phone}</p>
        <p className="text-sm text-gray-600">{resume.location}</p>
      </div>
      {resume.professional_summary && (
        <div>
          <h2 className="text-lg font-semibold mb-2">Professional Summary</h2>
          <p className="text-sm text-gray-700">{resume.professional_summary}</p>
        </div>
      )}
      {resume.work_experiences?.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-2">Experience</h2>
          {resume.work_experiences.map((exp: any, i: number) => (
            <div key={i} className="mb-3">
              <h3 className="font-semibold">{exp.title}</h3>
              <p className="text-sm text-gray-600">{exp.company}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Template Modal
function TemplateModal({ currentTemplate, onSelect, onClose }: any) {
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-6">
      <div className="bg-deepTech rounded-2xl border border-white/10 p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Choose Template</h2>
          <button onClick={onClose} className="text-techGray hover:text-white text-2xl">✕</button>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {TEMPLATES.map((template) => (
            <button
              key={template.id}
              onClick={() => onSelect(template.id)}
              className={`p-4 rounded-xl border-2 transition-all ${
                currentTemplate === template.id
                  ? 'border-forgePurple bg-forgePurple/10'
                  : 'border-white/10 bg-white/5 hover:border-white/30'
              }`}
            >
              <div className="aspect-[8.5/11] bg-white/10 rounded-lg mb-3 flex items-center justify-center">
                <span className="text-4xl">{template.id === 'professional' ? '📄' : template.id === 'modern' ? '✨' : template.id === 'creative' ? '🎨' : '📋'}</span>
              </div>
              <h3 className="font-semibold text-white">{template.name}</h3>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
