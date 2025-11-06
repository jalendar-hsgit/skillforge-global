import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import LiveTemplatePreview from './LiveTemplatePreview';
import SplitViewToggle from './SplitViewToggle';
import { Button } from '@/components/Button';
import { exportResumePDF, exportResumePDFFromPreview } from '@/lib/pdf';
import { 
  Save, Download, Eye, Layout as LayoutIcon, GripVertical, 
  Wand2, FileText, Check, Sparkles, ChevronDown, ChevronUp, 
  Linkedin, GitCompare, Palette 
} from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
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
import AIAssistantPanel from './AIAssistantPanel';
import ATSBreakdownModal from './ATSBreakdownModal';
import StylePanel from './StylePanel';
import ResumeComparisonModal from './ResumeComparisonModal';
import LinkedInImportModal from './LinkedInImportModal';
import CoverLetterModal from './CoverLetterModal';
import KeyboardShortcutsModal from './KeyboardShortcutsModal';
import ExportOptionsModal from './ExportOptionsModal';
import { useUndoRedo, UndoRedoControls, AutoSaveIndicator } from '@/hooks/useUndoRedo';
import { API_BASE } from '@/lib/apiBase';

interface Resume {
  id: number;
  user_id?: number;
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
  
  // Customization fields
  font_family?: string;
  color_theme?: string;
  layout?: string;
  accent_color?: string;
  picture_style?: string;
  show_icons?: boolean;
  background_type?: string;
  rating_style?: string;
  text_color?: string;
  heading_color?: string;
  line_spacing?: number;
  font_size?: number;
  heading_size?: number;
  
  created_at: string;
  updated_at: string;
}

interface Section {
  id: string;
  title: string;
  icon: string;
  enabled: boolean;
}

interface ResumeEditorProps {
  resumeId: number;
}

export default function ResumeEditor({ resumeId }: ResumeEditorProps) {
  const router = useRouter();
  
  // Undo/Redo state management
  const {
    state: resume,
    setState: setResumeWithHistory,
    undo,
    redo,
    canUndo,
    canRedo,
    history,
  } = useUndoRedo<Resume | null>(null, 50);
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'saving' | 'saved' | 'error' | 'idle'>('idle');
  const [saveError, setSaveError] = useState<string | undefined>();
  const [exporting, setExporting] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>('header');
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [showStylePanel, setShowStylePanel] = useState(false);
  const [showATSBreakdown, setShowATSBreakdown] = useState(false);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  const [showLinkedInModal, setShowLinkedInModal] = useState(false);
  const [showCoverLetterModal, setShowCoverLetterModal] = useState(false);
  const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [showExportOptions, setShowExportOptions] = useState(false);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [isSplitView, setIsSplitView] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('resume-editor-split-view')
      return saved ? saved === 'true' : true
    }
    return true
  });
  const [showLivePreview, setShowLivePreview] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('resume-editor-show-preview')
      return saved ? saved === 'true' : true
    }
    return true
  });
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const previewRef = useRef<HTMLDivElement | null>(null);
  
  const [sections, setSections] = useState<Section[]>(() => {
    const defaultSections: Section[] = [
      { id: 'header', title: 'Contact Info', icon: '👤', enabled: true },
      { id: 'summary', title: 'Professional Summary', icon: '📝', enabled: true },
      { id: 'experience', title: 'Work Experience', icon: '💼', enabled: true },
      { id: 'education', title: 'Education', icon: '🎓', enabled: true },
      { id: 'skills', title: 'Skills', icon: '⚡', enabled: true },
      { id: 'projects', title: 'Projects', icon: '🚀', enabled: true },
      { id: 'certificates', title: 'Certificates', icon: '🏆', enabled: false },
      { id: 'achievements', title: 'Achievements', icon: '⭐', enabled: false },
    ]
    
    // Load saved section order from localStorage
    if (typeof window !== 'undefined') {
      const savedOrder = localStorage.getItem(`resume-section-order-${resumeId}`)
      if (savedOrder) {
        try {
          const orderIds = JSON.parse(savedOrder) as string[]
          const orderedSections = orderIds
            .map(id => defaultSections.find(s => s.id === id))
            .filter(Boolean) as Section[]
          
          // Add any new sections that weren't in saved order
          const missingSections = defaultSections.filter(
            s => !orderIds.includes(s.id)
          )
          return [...orderedSections, ...missingSections]
        } catch (e) {
          console.error('Failed to parse section order:', e)
        }
      }
    }
    
    return defaultSections
  });
  
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Load resume data
  useEffect(() => {
    loadResume();
  }, [resumeId]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (resume) saveResume(resume)
      }
      // Ctrl/Cmd + Z to undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        if (canUndo) undo()
      }
      // Ctrl/Cmd + Y or Ctrl/Cmd + Shift + Z to redo
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault()
        if (canRedo) redo()
      }
      // Ctrl/Cmd + B to toggle split view
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault()
        const newValue = !isSplitView
        setIsSplitView(newValue)
        localStorage.setItem('resume-editor-split-view', newValue.toString())
      }
      // Ctrl/Cmd + P to open preview
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault()
        window.open(`/resumes/${resumeId}/preview`, '_blank')
      }
      // Ctrl/Cmd + Shift + A to toggle AI panel
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
        e.preventDefault()
        setShowAIPanel(!showAIPanel)
        if (!showAIPanel) setShowStylePanel(false)
      }
      // ? to toggle keyboard shortcuts
      if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault()
        setShowKeyboardShortcuts(!showKeyboardShortcuts)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [resumeId, isSplitView, showAIPanel, showKeyboardShortcuts, canUndo, canRedo, undo, redo, resume])

  const loadResume = async () => {
    try {
      setLoading(true);
      // Use Next.js proxy which forwards HttpOnly cookie automatically
      const response = await fetch(`/api/session/resumes?id=${resumeId}`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        // Normalize API -> UI field names
        const normalized: Resume = {
          ...data,
          template: data.template_id,
          professional_summary: data.summary,
          linkedin: data.linkedin_url,
          github: data.github_url,
          website: data.website_url,
        };
        setResumeWithHistory(normalized);
        fetchATSScore();
      } else if (response.status === 401) {
        router.push('/login?redirect=' + encodeURIComponent(`/resumes/${resumeId}`));
        return;
      } else {
        const errorText = await response.text();
        console.error('Failed to load resume:', response.status, errorText);
        setToast({ 
          type: 'error', 
          message: `Failed to load resume (${response.status}): ${errorText || 'Unknown error'}` 
        });
        // Show error in UI but don't block the editor
        setResumeWithHistory(null);
      }
    } catch (error: any) {
      console.error('Error loading resume:', error);
      setToast({ 
        type: 'error', 
        message: `Failed to load resume: ${error?.message || 'Network error'}` 
      });
      setResumeWithHistory(null);
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
      } else {
        // Hide badge gracefully when endpoint not available
        setAtsScore(null);
      }
    } catch (error) {
      console.error('Error fetching ATS score:', error);
      setAtsScore(null);
    }
  };

  // Map UI keys to API payload keys accepted by ResumeUpdate
  const toApiPatch = (data: Partial<Resume>): Record<string, any> => {
    const out: Record<string, any> = {};
    if (data.title !== undefined) out.title = data.title;
    if ((data as any).template !== undefined) out.template_id = (data as any).template;
    if (data.full_name !== undefined) out.full_name = data.full_name;
    if (data.email !== undefined) out.email = data.email;
    if (data.phone !== undefined) out.phone = data.phone;
    if (data.location !== undefined) out.location = data.location;
    if ((data as any).linkedin !== undefined) out.linkedin_url = (data as any).linkedin;
    if ((data as any).github !== undefined) out.github_url = (data as any).github;
    if ((data as any).website !== undefined) out.website_url = (data as any).website;
    if ((data as any).professional_summary !== undefined) out.summary = (data as any).professional_summary;
    // Style & layout persistence
    if ((data as any).font_family !== undefined) out.font_family = (data as any).font_family;
    if ((data as any).layout !== undefined) out.layout = (data as any).layout;
    if ((data as any).accent_color !== undefined) out.accent_color = (data as any).accent_color;
    if ((data as any).picture_style !== undefined) out.picture_style = (data as any).picture_style;
    if ((data as any).show_icons !== undefined) out.show_icons = (data as any).show_icons;
    if ((data as any).color_theme !== undefined) out.color_theme = (data as any).color_theme;
    if ((data as any).text_color !== undefined) out.text_color = (data as any).text_color;
    if ((data as any).heading_color !== undefined) out.heading_color = (data as any).heading_color;
    if ((data as any).line_spacing !== undefined) out.line_spacing = (data as any).line_spacing;
    if ((data as any).font_size !== undefined) out.font_size = (data as any).font_size;
    if ((data as any).heading_size !== undefined) out.heading_size = (data as any).heading_size;
    return out;
  };

  // Auto-save function with debounce
  const saveResume = useCallback(async (data: Partial<Resume>) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    setSaveStatus('saving');
    
    saveTimeoutRef.current = setTimeout(async () => {
      try {
        setSaving(true);
        const payload = toApiPatch(data);
        if (Object.keys(payload).length === 0) {
          setSaving(false);
          setSaveStatus('idle');
          return;
        }
        const response = await fetch(`/api/session/resumes?id=${resumeId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          setLastSaved(new Date());
          setSaveStatus('saved');
          fetchATSScore(); // Refresh ATS score after save
          setToast({ type: 'success', message: 'Changes saved' });
          setTimeout(() => setToast(null), 2200);
          // Reset to idle after showing "saved" for a moment
          setTimeout(() => setSaveStatus('idle'), 2000);
        } else {
          setSaveStatus('error');
          setSaveError('Failed to save');
        }
      } catch (error) {
        console.error('Error saving resume:', error);
        setSaveStatus('error');
        setSaveError(error instanceof Error ? error.message : 'Unknown error');
        setToast({ type: 'error', message: 'Failed to auto-save. Check your connection.' });
        setTimeout(() => setToast(null), 2800);
      } finally {
        setSaving(false);
      }
    }, 2000); // 2 second debounce
  }, [resumeId]);
  
  const saveVersion = async () => {
    try {
      const versionName = prompt('Enter a name for this version (e.g., "Final Draft", "Software Engineer v2"):');
      if (!versionName) return;

      const response = await fetch(`${API_BASE}/api/v1x/resume-comparison/versions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          resume_id: resumeId,
          version_name: versionName,
          description: `Snapshot created on ${new Date().toLocaleString()}`
        })
      });

      if (response.ok) {
        setToast({ type: 'success', message: `Version "${versionName}" saved!` });
        setTimeout(() => setToast(null), 2500);
      } else {
        throw new Error('Failed to save version');
      }
    } catch (error) {
      console.error('Error saving version:', error);
      setToast({ type: 'error', message: 'Failed to save version' });
      setTimeout(() => setToast(null), 2500);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setSections((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        const newOrder = arrayMove(items, oldIndex, newIndex);
        
        // Persist section order to localStorage
        const sectionOrder = newOrder.map(s => s.id)
        localStorage.setItem(`resume-section-order-${resumeId}`, JSON.stringify(sectionOrder))
        
        // Show feedback
        setToast({ type: 'success', message: 'Section order updated' })
        setTimeout(() => setToast(null), 2000)
        
        return newOrder;
      });
    }
  };

  // SortableSection component for drag-and-drop section reordering
  const SortableSection: React.FC<{ section: Section }> = ({ section }) => {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      transition,
    } = useSortable({ id: section.id });

    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
    };

    const isActive = activeSection === section.id;

    return (
      <div
        ref={setNodeRef}
        style={style}
        className={`group flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
          isActive
            ? 'bg-gradient-to-r from-forgePurple/30 to-neuralBlue/20 border-forgePurple shadow-lg shadow-forgePurple/20 scale-[1.02]'
            : 'bg-white/5 border-white/10 hover:border-white/30 hover:bg-white/10 hover:shadow-md'
        }`}
      >
        <button
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing p-1.5 hover:bg-white/20 rounded-lg transition-colors"
        >
          <GripVertical className={`w-4 h-4 ${isActive ? 'text-white' : 'text-techGray group-hover:text-white'} transition-colors`} />
        </button>
        <button
          onClick={() => setActiveSection(section.id)}
          className="flex-1 text-left font-semibold text-sm tracking-wide flex items-center gap-2.5"
          style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}
        >
          <span className="text-lg">{section.icon}</span>
          <span className={isActive ? 'text-white' : 'text-techGray/90 group-hover:text-white'}>{section.title}</span>
        </button>
        <input
          type="checkbox"
          checked={section.enabled}
          onChange={(e) => {
            setSections(prev =>
              prev.map(s => s.id === section.id ? { ...s, enabled: e.target.checked } : s)
            );
          }}
          className="w-5 h-5 rounded border-2 border-white/20 bg-white/5 checked:bg-forgePurple checked:border-forgePurple cursor-pointer transition-all"
        />
      </div>
    );
  };

  // Update resume data and trigger auto-save
  const updateResume = (updates: Partial<Resume>) => {
    setResumeWithHistory(prev => {
      if (!prev) return prev;
      const updated = { ...prev, ...updates };
      saveResume(updates);
      return updated;
    });
  };

  const handleTemplateChange = (template: { id: number; name: string; config: any }) => {
    // Update resume with template ID and apply full template config
    const configUpdates = template.config ? {
      font_family: template.config.font_family || template.config.font || resume?.font_family,
      layout: template.config.layout || resume?.layout,
      accent_color: template.config.accent_color || template.config.accent || resume?.accent_color,
      picture_style: template.config.picture_style || template.config.picture || resume?.picture_style,
      show_icons: template.config.show_icons !== undefined ? template.config.show_icons : (template.config.icons !== undefined ? template.config.icons : resume?.show_icons),
      color_theme: template.config.color_theme || resume?.color_theme,
    } : {};

    updateResume({ 
      template: template.id.toString(),
      ...configUpdates
    });
    
    setShowTemplateSelector(false);
    setToast({ type: 'success', message: `Applied template: ${template.name}` });
    setTimeout(() => setToast(null), 2500);
    
    // Track template change event & popularity
    if (template.id) {
      // Fire-and-forget analytics; ignore failures in editor UX
      fetch(`${API_BASE}/api/v1x/resume-templates/${template.id}/popularity`, { 
        method: 'POST',
        credentials: 'include' 
      }).catch(() => {});
      
      if (resume?.id && resume?.user_id) {
        fetch(`${API_BASE}/api/v1x/resume-analytics/events/template/${resume.id}?user_id=${resume.user_id}&template_id=${template.id}`, { 
          method: 'POST',
          credentials: 'include'
        }).catch(() => {});
      }
    }
  };

  if (loading) {
    return (
      <Layout showFooter={false}>
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90">
          <div className="text-center">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-forgePurple/20 border-t-forgePurple mx-auto mb-6"></div>
              <div className="absolute inset-0 animate-pulse">
                <div className="rounded-full h-16 w-16 bg-forgePurple/10 mx-auto"></div>
              </div>
            </div>
            <p className="text-lg font-bold text-white tracking-wide mb-2" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
              Loading your resume...
            </p>
            <p className="text-sm text-techGray/80 font-medium">Just a moment</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!resume && !loading) {
    return (
      <Layout showFooter={false}>
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90">
          <div className="text-center max-w-md px-6">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-white mb-3">Resume Not Found</h2>
            <p className="text-techGray mb-6">
              {toast?.message || 'The resume could not be loaded. It may have been deleted or you may not have permission to view it.'}
            </p>
            <div className="flex gap-3 justify-center">
              <Button onClick={() => router.push('/dashboard')} variant="primary">
                Go to Dashboard
              </Button>
              <Button onClick={() => loadResume()} variant="secondary">
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // TypeScript type narrowing: resume is guaranteed to be non-null here
  if (!resume) return null;

  return (
    <Layout showFooter={false} maxWidth="full">
      {/* Top Action Bar */}
      <div className="bg-gradient-to-r from-forgePurple/20 via-neuralBlue/20 to-forgePurple/20 border-b border-white/20 sticky top-0 z-50 backdrop-blur-xl shadow-lg">
        <div className="max-w-[2000px] mx-auto px-8 py-5 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <button
              onClick={() => router.push('/dashboard')}
              className="flex items-center gap-2 text-techGray hover:text-white transition-all duration-200 font-medium group"
            >
              <span className="transform group-hover:-translate-x-1 transition-transform">←</span>
              <span className="hidden sm:inline">Back</span>
            </button>
            <div className="border-l border-white/20 h-8"></div>
            <div>
              <input
                type="text"
                value={resume?.title || ''}
                onChange={(e) => updateResume({ title: e.target.value })}
                className="text-2xl font-bold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-forgePurple/50 rounded-lg px-3 py-1.5 transition-all placeholder:text-techGray/50 tracking-tight"
                placeholder="My Professional Resume"
                data-testid="input-title"
                style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Auto-save Indicator */}
            <AutoSaveIndicator status={saveStatus} />
            
            {/* Undo/Redo Controls */}
            <UndoRedoControls
              onUndo={undo}
              onRedo={redo}
              canUndo={canUndo}
              canRedo={canRedo}
              historyCount={history.length}
            />
            
            {/* Keyboard Shortcuts Button */}
            <button
              onClick={() => setShowKeyboardShortcuts(true)}
              className="p-2 hover:bg-white/10 rounded-lg transition-all text-white/60 hover:text-white group"
              title="Keyboard Shortcuts (?)"
            >
              <span className="text-lg group-hover:scale-110 transition-transform inline-block">⌨️</span>
            </button>
            
            {/* ATS Score Badge */}
            {atsScore !== null && (
              <button
                onClick={() => setShowATSBreakdown(true)}
                className={`px-5 py-3 rounded-xl border-2 backdrop-blur-sm transition-all duration-300 hover:scale-105 cursor-pointer ${
                  atsScore >= 80 ? 'bg-gradient-to-br from-green-500/30 to-green-600/20 border-green-400/50 text-green-100 shadow-lg shadow-green-500/20 hover:shadow-green-500/40' :
                  atsScore >= 60 ? 'bg-gradient-to-br from-yellow-500/30 to-yellow-600/20 border-yellow-400/50 text-yellow-100 shadow-lg shadow-yellow-500/20 hover:shadow-yellow-500/40' :
                  'bg-gradient-to-br from-red-500/30 to-red-600/20 border-red-400/50 text-red-100 shadow-lg shadow-red-500/20 hover:shadow-red-500/40'
                }`}
                title="Click for detailed analysis"
              >
                <div className="text-[10px] font-bold uppercase tracking-wider opacity-80">ATS Score</div>
                <div className="text-2xl font-black tracking-tight mt-0.5">{atsScore}%</div>
              </button>
            )}
            <Button
              onClick={async () => {
                if (!resume || saving) return;
                try {
                  setSaving(true);
                  // Lightweight validation before save
                  const errs: string[] = [];
                  if (resume.email && !/^\S+@\S+\.\S+$/.test(resume.email)) errs.push('Enter a valid email');
                  if (resume.phone) {
                    const digits = (resume.phone.match(/\d/g) || []).length;
                    if (digits > 0 && digits < 8) errs.push('Phone looks too short');
                  }
                  if (errs.length) {
                    setToast({ type: 'error', message: errs[0] });
                    setTimeout(() => setToast(null), 2600);
                    setSaving(false);
                    return;
                  }
                  // Build minimal, valid PATCH payload matching backend schema
                  const payload: Record<string, any> = {
                    title: resume.title,
                    template_id: (resume as any).template,
                    full_name: resume.full_name,
                    email: (resume as any).email,
                    phone: (resume as any).phone,
                    location: (resume as any).location,
                    linkedin_url: (resume as any).linkedin,
                    github_url: (resume as any).github,
                    website_url: (resume as any).website,
                    summary: (resume as any).professional_summary,
                  };
                  const response = await fetch(`/api/session/resumes?id=${resumeId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(payload),
                  });
                  if (response.ok) {
                    setLastSaved(new Date());
                    fetchATSScore();
                    setToast({ type: 'success', message: 'Saved successfully' });
                    setTimeout(() => setToast(null), 2000);
                  } else {
                    const txt = await response.text();
                    console.error('Save failed:', response.status, txt);
                    setToast({ type: 'error', message: 'Failed to save resume' });
                    setTimeout(() => setToast(null), 2800);
                  }
                } catch (error) {
                  console.error('Error saving resume:', error);
                  setToast({ type: 'error', message: 'Failed to save resume' });
                  setTimeout(() => setToast(null), 2800);
                } finally {
                  setSaving(false);
                }
              }}
              variant="secondary"
              disabled={saving}
              data-testid="btn-save"
              className="font-semibold transition-all duration-200 hover:shadow-lg bg-green-500/20 border-green-400/50 hover:bg-green-500/30"
            >
              {saving ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  <span className="tracking-wide">Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  <span className="tracking-wide">Save</span>
                </>
              )}
            </Button>
            <Button
              onClick={() => {
                setShowAIPanel(!showAIPanel);
                if (!showAIPanel) setShowStylePanel(false);
              }}
              variant="secondary"
              data-testid="btn-ai-panel"
              className={`font-semibold transition-all duration-200 hover:shadow-lg ${showAIPanel ? 'bg-forgePurple/30 border-forgePurple' : ''}`}
            >
              <Wand2 className="w-4 h-4 mr-2" />
              <span className="tracking-wide">AI Assistant</span>
            </Button>
            <Button
              onClick={() => {
                setShowStylePanel(!showStylePanel);
                if (!showStylePanel) setShowAIPanel(false);
              }}
              variant="secondary"
              data-testid="btn-styles"
              className={`font-semibold transition-all duration-200 hover:shadow-lg ${showStylePanel ? 'bg-neuralBlue/30 border-neuralBlue' : ''}`}
            >
              <Palette className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Styles</span>
            </Button>
            <Button
              onClick={() => setShowCoverLetterModal(true)}
              variant="secondary"
              className="font-semibold transition-all duration-200 hover:shadow-lg bg-purple-500/20 border-purple-400/50 hover:bg-purple-500/30"
            >
              <FileText className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Cover Letter</span>
            </Button>
            <Button
              onClick={saveVersion}
              variant="secondary"
              className="font-semibold transition-all duration-200 hover:shadow-lg bg-blue-500/20 border-blue-400/50 hover:bg-blue-500/30"
            >
              <Save className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Save Version</span>
            </Button>
            <Button
              onClick={() => setShowComparisonModal(true)}
              variant="secondary"
              className="font-semibold transition-all duration-200 hover:shadow-lg"
            >
              <GitCompare className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Compare</span>
            </Button>
            <Button
              onClick={() => setShowLinkedInModal(true)}
              variant="secondary"
              className="font-semibold transition-all duration-200 hover:shadow-lg bg-[#0077B5]/20 border-[#0077B5]/50 hover:bg-[#0077B5]/30"
            >
              <Linkedin className="w-4 h-4 mr-2" />
              <span className="tracking-wide">LinkedIn</span>
            </Button>
            <Button
              onClick={() => setShowTemplateSelector(true)}
              variant="secondary"
              className="font-semibold transition-all duration-200 hover:shadow-lg"
            >
              <LayoutIcon className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Templates</span>
            </Button>
            
            <SplitViewToggle 
              isSplitView={isSplitView} 
              onToggle={() => {
                const newValue = !isSplitView
                setIsSplitView(newValue)
                localStorage.setItem('resume-editor-split-view', newValue.toString())
              }} 
            />
            
            <Button
              onClick={() => window.open(`/resumes/${resumeId}/preview`, '_blank')}
              variant="secondary"
              data-testid="btn-full-preview"
              className="font-semibold transition-all duration-200 hover:shadow-lg"
            >
              <Eye className="w-4 h-4 mr-2" />
              <span className="tracking-wide">Preview</span>
            </Button>
            <Button
              onClick={() => setShowExportOptions(true)}
              variant="primary"
              data-testid="btn-export"
              className="font-bold tracking-wide transition-all duration-200 hover:shadow-xl hover:scale-105"
            >
              <Download className="w-4 h-4 mr-2" />
              <span>Export</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Editor Layout */}
      <div className="flex h-[calc(100vh-140px)]">
        {/* Left Sidebar - Draggable Section Navigator */}
        <div className="w-80 bg-gradient-to-b from-deepTech via-deepTech/95 to-deepTech/90 border-r border-white/20 overflow-y-auto shadow-2xl">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
              <h3 className="text-xs font-black text-white uppercase tracking-[0.15em] flex items-center gap-2" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                <FileText className="w-4 h-4 text-forgePurple" />
                Resume Sections
              </h3>
              <GripVertical className="w-4 h-4 text-techGray/50" />
            </div>
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={sections.map(s => s.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="space-y-3">
                  {sections.map((section) => (
                    <SortableSection key={section.id} section={section} />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
            <div className="mt-8 pt-6 border-t border-white/10">
              <p className="text-xs text-techGray/60 text-center font-medium tracking-wide" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                💡 Drag sections to reorder
              </p>
            </div>
          </div>
        </div>

        {/* Center - Editor Forms */}
        <div className="flex-1 overflow-y-auto bg-gradient-to-br from-deepTech/40 via-deepTech/30 to-deepTech/40 p-10">
          <div className="max-w-4xl mx-auto">
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

        {/* Right Sidebar - AI Panel or Live Preview */}
        <div className="w-[32rem] bg-gradient-to-b from-deepTech via-deepTech/95 to-deepTech/90 border-l border-white/20 overflow-y-auto shadow-2xl">
          {showAIPanel ? (
            <div className="p-6 h-full flex flex-col">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                <h3 className="text-xl font-black flex items-center gap-3" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                  <div className="p-2 bg-gradient-to-br from-forgePurple to-neuralBlue rounded-lg">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent">
                    AI Assistant
                  </span>
                </h3>
                <button
                  onClick={() => setShowAIPanel(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group"
                >
                  <ChevronUp className="w-5 h-5 text-techGray group-hover:text-white transition-colors" />
                </button>
              </div>
              <AIAssistantPanel
                resume={resume}
                resumeId={String(resumeId)}
                onClose={() => setShowAIPanel(false)}
                onApply={(field, value) => {
                  updateResume({ [field]: value });
                  setShowAIPanel(false);
                }}
              />
            </div>
          ) : showStylePanel ? (
            <div className="p-6 h-full flex flex-col">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                <h3 className="text-xl font-black flex items-center gap-3" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                  <div className="p-2 bg-gradient-to-br from-neuralBlue to-forgePurple rounded-lg">
                    <Palette className="w-5 h-5 text-white" />
                  </div>
                  <span className="bg-gradient-to-r from-neuralBlue via-forgePurple to-neuralBlue bg-clip-text text-transparent">
                    Style Settings
                  </span>
                </h3>
                <button
                  onClick={() => setShowStylePanel(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group"
                >
                  <ChevronUp className="w-5 h-5 text-techGray group-hover:text-white transition-colors" />
                </button>
              </div>
              <div className="overflow-y-auto flex-1">
                <StylePanel resume={resume} onUpdate={(updates) => updateResume(updates)} />
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                <h3 className="text-xs font-black text-white uppercase tracking-[0.15em] flex items-center gap-2" data-testid="editor-live-preview" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                  <Eye className="w-4 h-4 text-neuralBlue" />
                  Live Preview
                </h3>
              </div>
              <div className="bg-gradient-to-br from-white/5 to-white/10 rounded-2xl p-4 border border-white/20 shadow-2xl">
                <div ref={previewRef} className="bg-white rounded-xl shadow-2xl overflow-hidden" style={{ transform: 'scale(0.72)', transformOrigin: 'top left', width: '139%' }}>
                  <ResumePreview resume={resume} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Template Gallery Modal */}
        {showTemplateSelector && (
          <TemplateSelector
            onSelect={handleTemplateChange}
            onClose={() => setShowTemplateSelector(false)}
            resumeData={resume}
            currentTemplate={resume?.template ? Number(resume.template) : undefined}
          />
        )}      {/* ATS Breakdown Modal */}
      {showATSBreakdown && (
        <ATSBreakdownModal
          resumeId={String(resumeId)}
          onClose={() => setShowATSBreakdown(false)}
        />
      )}

      {/* Resume Comparison Modal */}
      {showComparisonModal && (
        <ResumeComparisonModal
          isOpen={showComparisonModal}
          onClose={() => setShowComparisonModal(false)}
          resumeId={resumeId}
        />
      )}

      {/* LinkedIn Import Modal */}
      {showLinkedInModal && (
        <LinkedInImportModal
          isOpen={showLinkedInModal}
          onClose={() => setShowLinkedInModal(false)}
          resumeId={resumeId}
          onImportComplete={(newResumeId) => {
            setShowLinkedInModal(false);
            if (newResumeId !== resumeId) {
              router.push(`/resumes/${newResumeId}`);
            } else {
              loadResume();
            }
          }}
        />
      )}

      {/* Cover Letter Modal */}
      {showCoverLetterModal && (
        <CoverLetterModal
          isOpen={showCoverLetterModal}
          onClose={() => setShowCoverLetterModal(false)}
          resumeId={resumeId}
        />
      )}

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal
        isOpen={showKeyboardShortcuts}
        onClose={() => setShowKeyboardShortcuts(false)}
      />

      {/* Export Options Modal */}
      <ExportOptionsModal
        isOpen={showExportOptions}
        onClose={() => setShowExportOptions(false)}
        resume={resume}
        resumeId={resumeId}
      />

      {/* Toasts */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-[60]">
          <div
            className={`min-w-[240px] max-w-sm px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-sm transition-all ${
              toast.type === 'success'
                ? 'bg-green-500/20 border-green-400/40 text-green-100'
                : toast.type === 'error'
                ? 'bg-red-500/20 border-red-400/40 text-red-100'
                : 'bg-blue-500/20 border-blue-400/40 text-blue-100'
            }`}
            role="status"
            aria-live="polite"
          >
            <p className="text-sm font-semibold tracking-wide" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
              {toast.message}
            </p>
          </div>
        </div>
      )}

      {/* Subtle bottom saved indicator */}
      <div className="fixed bottom-3 left-1/2 -translate-x-1/2 md:left-auto md:right-[34rem] z-40">
        <div className="px-3 py-1.5 rounded-full text-xs font-medium bg-white/5 border border-white/10 text-white/70 backdrop-blur-sm shadow-lg">
          {saving ? 'Saving…' : lastSaved ? `Saved ${lastSaved.toLocaleTimeString()}` : '—'}
        </div>
      </div>
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

  const [localToast, setLocalToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const generateSummary = async () => {
    setGenerating(true);
    setShowAISuggestions(true);
    try {
      const response = await fetch(`/api/session/resume-ai/professional-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: resume.title || 'Software Engineer',
          years_of_experience: 3,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Backend returns { summary, variations }
        const list = Array.isArray(data.variations) && data.variations.length > 0
          ? data.variations
          : (data.summary ? [data.summary] : []);
        setSuggestions(list);
        setLocalToast({ type: 'success', message: 'AI suggestions ready' });
        setTimeout(() => setLocalToast(null), 2200);
      } else if (response.status === 401) {
        setLocalToast({ type: 'error', message: 'Please log in to use AI' });
        setTimeout(() => setLocalToast(null), 2600);
      } else {
        setLocalToast({ type: 'error', message: 'AI service unavailable' });
        setTimeout(() => setLocalToast(null), 2600);
      }
    } catch (error) {
      console.error('Error generating summary:', error);
      setLocalToast({ type: 'error', message: 'Failed to generate summary' });
      setTimeout(() => setLocalToast(null), 2600);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
          Professional Summary
        </h2>
        <Button onClick={generateSummary} variant="secondary" disabled={generating} data-testid="btn-ai-generate" className="font-semibold">
          {generating ? '⏳ Generating...' : '✨ AI Generate'}
        </Button>
      </div>
      <p className="text-sm text-techGray/80 leading-relaxed">
        Write a compelling 2–3 sentence summary that highlights your key strengths and career goals.
      </p>
      <textarea
        value={resume.professional_summary || ''}
        onChange={(e) => updateResume({ professional_summary: e.target.value })}
        rows={6}
        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-techGray/60 focus:outline-none focus:ring-2 focus:ring-forgePurple/40 focus:border-transparent shadow-inner"
        placeholder="e.g., Results-driven Software Engineer with 5+ years of experience building scalable web applications..."
      />
      {showAISuggestions && suggestions.length > 0 && (
        <Card className="p-4 bg-white/5 border-white/10" data-testid="ai-suggestions">
          <h4 className="font-semibold text-white mb-3">AI Suggestions</h4>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  updateResume({ professional_summary: suggestion });
                  setShowAISuggestions(false);
                }}
                className="w-full text-left p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all border border-white/10"
              >
                <p className="text-sm text-techGray/90 leading-relaxed">{suggestion}</p>
              </button>
            ))}
          </div>
        </Card>
      )}

      {localToast && (
        <div className="fixed bottom-6 right-[28rem] z-[60]">
          <div
            className={`min-w-[220px] max-w-sm px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-sm transition-all ${
              localToast.type === 'success'
                ? 'bg-green-500/20 border-green-400/40 text-green-100'
                : localToast.type === 'error'
                ? 'bg-red-500/20 border-red-400/40 text-red-100'
                : 'bg-blue-500/20 border-blue-400/40 text-blue-100'
            }`}
            role="status"
            aria-live="polite"
          >
            <p className="text-sm font-semibold tracking-wide" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
              {localToast.message}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
