import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { exportResumePDF, exportResumePDFFromPreview } from '@/lib/pdf';
import ResumeHeader from './ResumeHeader';
import WorkExperienceSection from './WorkExperienceSection';
import EducationSection from './EducationSection';
import SkillsSection from './SkillsSection';
import ProjectsSection from './ProjectsSection';
import CertificatesSection from './CertificatesSection';
import AchievementsSection from './AchievementsSection';
import ResumePreview from './ResumePreview';
import ATSScoreCard from './ATSScoreCard';
import TemplateSelector from './TemplateSelector';

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

interface ResumeEditorProps {
  resumeId: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function ResumeEditor({ resumeId }: ResumeEditorProps) {
  const router = useRouter();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>('header');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previewRef = useRef<HTMLDivElement | null>(null);

  // Load resume data
  useEffect(() => {
    loadResume();
  }, [resumeId]);

  const loadResume = async () => {
    try {
      setLoading(true);
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${API_BASE}/api/v1x/resumes/${resumeId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setResume(data);
      } else {
        console.error('Failed to load resume');
        alert('Failed to load resume');
      }
    } catch (error) {
      console.error('Error loading resume:', error);
      alert('Failed to load resume');
    } finally {
      setLoading(false);
    }
  };

  // Auto-save function with debounce
  const saveResume = useCallback(async (data: Partial<Resume>) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(async () => {
      try {
        setSaving(true);
        const token = document.cookie
          .split('; ')
          .find(row => row.startsWith('token='))
          ?.split('=')[1];

        if (!token) return;

        const response = await fetch(`${API_BASE}/api/v1x/resumes/${resumeId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          setLastSaved(new Date());
        }
      } catch (error) {
        console.error('Error saving resume:', error);
      } finally {
        setSaving(false);
      }
    }, 3000); // 3 second debounce
  }, [resumeId]);

  // Update resume data and trigger auto-save
  const updateResume = (updates: Partial<Resume>) => {
    setResume(prev => {
      if (!prev) return prev;
      const updated = { ...prev, ...updates };
      saveResume(updates);
      return updated;
    });
  };

  const handleTemplateChange = (template: string) => {
    updateResume({ template });
    setShowTemplateSelector(false);
  };

  if (loading || !resume) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading resume...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Header Bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-[1800px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Back
            </button>
            <div>
              <input
                type="text"
                value={resume.title}
                onChange={(e) => updateResume({ title: e.target.value })}
                className="text-xl font-semibold text-gray-900 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
                placeholder="Resume Title"
              />
              <p className="text-sm text-gray-500 mt-1">
                {saving ? (
                  <span className="flex items-center gap-2">
                    <span className="animate-spin">⏳</span> Saving...
                  </span>
                ) : lastSaved ? (
                  `Last saved ${lastSaved.toLocaleTimeString()}`
                ) : (
                  'Not saved yet'
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => setShowTemplateSelector(true)}
              variant="secondary"
            >
              🎨 Change Template
            </Button>
            <Button
              onClick={() => window.open(`/resumes/${resumeId}/preview`, '_blank')}
              variant="secondary"
            >
              👁️ Full Preview
            </Button>
            <Button
              onClick={async () => {
                if (!resume) return;
                try {
                  setExporting(true);
                  const safeTitle = (resume.title || 'Resume').replace(/\s+/g, '_').trim();
                  await exportResumePDFFromPreview(resumeId, `${safeTitle}.pdf`);
                } catch (e) {
                  console.error('PDF export failed', e);
                  alert('Failed to export PDF. Try using the Full Preview page and print to PDF.');
                } finally {
                  setExporting(false);
                }
              }}
              variant="primary"
              disabled={exporting}
            >
              {exporting ? '⏳ Exporting…' : '📄 Export PDF'}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Editor Layout */}
      <div className="flex h-[calc(100vh-140px)]">
        {/* Left Sidebar - Section Navigator */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto">
          <div className="p-4 space-y-2">
            <SectionButton
              active={activeSection === 'header'}
              onClick={() => setActiveSection('header')}
              icon="👤"
              label="Header & Contact"
            />
            <SectionButton
              active={activeSection === 'summary'}
              onClick={() => setActiveSection('summary')}
              icon="📝"
              label="Professional Summary"
            />
            <SectionButton
              active={activeSection === 'experience'}
              onClick={() => setActiveSection('experience')}
              icon="💼"
              label="Work Experience"
            />
            <SectionButton
              active={activeSection === 'education'}
              onClick={() => setActiveSection('education')}
              icon="🎓"
              label="Education"
            />
            <SectionButton
              active={activeSection === 'skills'}
              onClick={() => setActiveSection('skills')}
              icon="⚡"
              label="Skills"
            />
            <SectionButton
              active={activeSection === 'projects'}
              onClick={() => setActiveSection('projects')}
              icon="🚀"
              label="Projects"
            />
            <SectionButton
              active={activeSection === 'certificates'}
              onClick={() => setActiveSection('certificates')}
              icon="🏆"
              label="Certificates"
            />
            <SectionButton
              active={activeSection === 'achievements'}
              onClick={() => setActiveSection('achievements')}
              icon="⭐"
              label="Achievements"
            />
          </div>
        </div>

        {/* Center - Editor Forms */}
        <div className="flex-1 overflow-y-auto bg-white p-8">
          <div className="max-w-3xl mx-auto">
            {activeSection === 'header' && (
              <ResumeHeader resume={resume} updateResume={updateResume} />
            )}
            {activeSection === 'summary' && (
              <ProfessionalSummarySection resume={resume} updateResume={updateResume} />
            )}
            {activeSection === 'experience' && (
              <WorkExperienceSection
                resumeId={resumeId}
                experiences={resume.work_experiences}
                onUpdate={loadResume}
              />
            )}
            {activeSection === 'education' && (
              <EducationSection
                resumeId={resumeId}
                education={resume.education}
                onUpdate={loadResume}
              />
            )}
            {activeSection === 'skills' && (
              <SkillsSection
                resumeId={resumeId}
                skills={resume.skills}
                onUpdate={loadResume}
              />
            )}
            {activeSection === 'projects' && (
              <ProjectsSection
                resumeId={resumeId}
                projects={resume.projects}
                onUpdate={loadResume}
              />
            )}
            {activeSection === 'certificates' && (
              <CertificatesSection
                resumeId={resumeId}
                certificates={resume.certificates}
                onUpdate={loadResume}
              />
            )}
            {activeSection === 'achievements' && (
              <AchievementsSection
                resumeId={resumeId}
                achievements={resume.achievements}
                onUpdate={loadResume}
              />
            )}
          </div>
        </div>

        {/* Right Sidebar - Preview & ATS Score */}
        <div className="w-96 bg-gray-50 border-l border-gray-200 overflow-y-auto">
          <div className="p-4 space-y-4">
            <ATSScoreCard resumeId={resumeId} />
            <Card className="p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Live Preview</h3>
              <div ref={previewRef} className="bg-white p-4 rounded">
                <ResumePreview resume={resume} />
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Template Selector Modal */}
      {showTemplateSelector && (
        <TemplateSelector
          currentTemplate={resume.template}
          onSelect={handleTemplateChange}
          onClose={() => setShowTemplateSelector(false)}
        />
      )}
    </Layout>
  );
}

// Section Button Component
interface SectionButtonProps {
  active: boolean;
  onClick: () => void;
  icon: string;
  label: string;
}

function SectionButton({ active, onClick, icon, label }: SectionButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all ${
        active
          ? 'bg-blue-600 text-white shadow-sm'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <span className="text-xl">{icon}</span>
      <span className="font-medium text-sm">{label}</span>
    </button>
  );
}

// Professional Summary Section Component
interface ProfessionalSummarySectionProps {
  resume: Resume;
  updateResume: (updates: Partial<Resume>) => void;
}

function ProfessionalSummarySection({ resume, updateResume }: ProfessionalSummarySectionProps) {
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const generateSummary = async () => {
    setGenerating(true);
    setShowAISuggestions(true);
    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(`${API_BASE}/api/v1x/resume-ai/professional-summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: resume.title || 'Software Engineer',
          years_of_experience: 3,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.summaries || []);
      }
    } catch (error) {
      console.error('Error generating summary:', error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Professional Summary</h2>
        <Button onClick={generateSummary} variant="secondary" disabled={generating}>
          {generating ? '⏳ Generating...' : '✨ AI Generate'}
        </Button>
      </div>
      <p className="text-gray-600">
        Write a compelling 2-3 sentence summary that highlights your key strengths and career goals.
      </p>
      <textarea
        value={resume.professional_summary || ''}
        onChange={(e) => updateResume({ professional_summary: e.target.value })}
        rows={6}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="e.g., Results-driven Software Engineer with 5+ years of experience building scalable web applications..."
      />
      {showAISuggestions && suggestions.length > 0 && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <h4 className="font-semibold text-gray-900 mb-3">AI Suggestions:</h4>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  updateResume({ professional_summary: suggestion });
                  setShowAISuggestions(false);
                }}
                className="w-full text-left p-3 bg-white rounded-lg hover:shadow-md transition-all border border-gray-200"
              >
                <p className="text-sm text-gray-700">{suggestion}</p>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
