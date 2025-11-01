import { useState } from 'react';
import { Wand2, Sparkles, FileText, Key, Lightbulb, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/Button';

interface Resume {
  id: number;
  title: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  summary?: string;
  work_experiences?: any[];
  education?: any[];
  skills?: string[];
  projects?: any[];
  certificates?: any[];
  achievements?: any[];
}

interface AIAssistantPanelProps {
  resume: Resume;
  resumeId: string;
  onClose: () => void;
  onApply: (field: string, value: any) => void;
}

type TabType = 'bullets' | 'summary' | 'keywords' | 'projects';

export default function AIAssistantPanel({ resume, resumeId, onClose, onApply }: AIAssistantPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>('summary');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const tabs = [
    { id: 'summary' as TabType, label: 'Summary', icon: FileText, description: 'Generate professional summary' },
    { id: 'bullets' as TabType, label: 'Bullets', icon: Sparkles, description: 'Enhance bullet points' },
    { id: 'keywords' as TabType, label: 'Keywords', icon: Key, description: 'Optimize keywords' },
    { id: 'projects' as TabType, label: 'Projects', icon: Lightbulb, description: 'Get project ideas' },
  ];

  const generateSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      // Extract years of experience from work history
      const yearsOfExperience = resume.work_experiences?.length 
        ? Math.max(1, resume.work_experiences.length * 2) 
        : 2;
      
      const response = await fetch('/api/session/resume-ai/professional-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: resume.title || 'Professional',
          years_of_experience: yearsOfExperience,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate summary');
      
      const data = await response.json();
      setSuggestions([{ type: 'summary', content: data.summary }]);
    } catch (err: any) {
      setError(err.message || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  const generateBullets = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get the most recent work experience
      const latestJob = resume.work_experiences?.[0];
      if (!latestJob) {
        setError('Add work experience first to generate bullets');
        setLoading(false);
        return;
      }

      const response = await fetch('/api/session/resume-ai/bullets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          job_title: latestJob.title || 'Professional',
          company: latestJob.company || 'Company',
          description: latestJob.description || '',
        }),
      });

      if (!response.ok) throw new Error('Failed to generate bullets');
      
      const data = await response.json();
      setSuggestions(data.bullets.map((bullet: string) => ({ type: 'bullet', content: bullet })));
    } catch (err: any) {
      setError(err.message || 'Failed to generate bullets');
    } finally {
      setLoading(false);
    }
  };

  const generateKeywords = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use summary or title as job description
      const jobDescription = resume.summary || resume.title || 'Professional resume';

      const response = await fetch('/api/session/resume-ai/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          job_description: jobDescription,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate keywords');
      
      const data = await response.json();
      setSuggestions(data.keywords.map((keyword: string) => ({ type: 'keyword', content: keyword })));
    } catch (err: any) {
      setError(err.message || 'Failed to generate keywords');
    } finally {
      setLoading(false);
    }
  };

  const generateProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/session/resume-ai/project-ideas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          skill_level: 'intermediate',
        }),
      });

      if (!response.ok) throw new Error('Failed to generate projects');
      
      const data = await response.json();
      setSuggestions(data.projects.map((project: any) => ({ 
        type: 'project', 
        content: project.title,
        description: project.description,
        tech_stack: project.tech_stack 
      })));
    } catch (err: any) {
      setError(err.message || 'Failed to generate projects');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = () => {
    setSuggestions([]);
    setError(null);
    
    switch (activeTab) {
      case 'summary':
        generateSummary();
        break;
      case 'bullets':
        generateBullets();
        break;
      case 'keywords':
        generateKeywords();
        break;
      case 'projects':
        generateProjects();
        break;
    }
  };

  const handleApplySuggestion = (suggestion: any) => {
    switch (suggestion.type) {
      case 'summary':
        onApply('summary', suggestion.content);
        break;
      case 'keyword':
        // Add to skills array
        const currentSkills = resume.skills || [];
        if (!currentSkills.includes(suggestion.content)) {
          onApply('skills', [...currentSkills, suggestion.content]);
        }
        break;
      case 'bullet':
      case 'project':
        // These would need more complex handling
        // For now, just copy to clipboard
        navigator.clipboard.writeText(suggestion.content);
        alert('Copied to clipboard!');
        break;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="grid grid-cols-2 gap-2 mb-6">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setSuggestions([]);
                setError(null);
              }}
              className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                isActive
                  ? 'bg-gradient-to-br from-forgePurple/30 to-neuralBlue/20 border-forgePurple shadow-lg'
                  : 'bg-white/5 border-white/10 hover:border-white/30 hover:bg-white/10'
              }`}
              style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className={`w-4 h-4 ${isActive ? 'text-forgePurple' : 'text-techGray'}`} />
                <span className={`font-bold text-sm ${isActive ? 'text-white' : 'text-techGray'}`}>
                  {tab.label}
                </span>
              </div>
              <p className={`text-xs ${isActive ? 'text-techGray/90' : 'text-techGray/60'}`}>
                {tab.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={loading}
          variant="primary"
          className="w-full mb-4 font-bold tracking-wide"
          data-testid="btn-ai-generate"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Wand2 className="w-4 h-4 mr-2" />
              Generate {tabs.find(t => t.id === activeTab)?.label}
            </>
          )}
        </Button>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/20 border-2 border-red-500/50 rounded-xl p-4 mb-4">
            <p className="text-sm text-red-200 font-medium">{error}</p>
          </div>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="space-y-3" data-testid="ai-suggestions">
            <h4 className="text-xs font-black uppercase tracking-wider text-techGray flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              Suggestions Ready
            </h4>
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 hover:border-white/20 transition-all duration-200 group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm text-white font-medium leading-relaxed mb-2">
                      {suggestion.content}
                    </p>
                    {suggestion.description && (
                      <p className="text-xs text-techGray/80 mb-2">
                        {suggestion.description}
                      </p>
                    )}
                    {suggestion.tech_stack && (
                      <div className="flex flex-wrap gap-1.5">
                        {suggestion.tech_stack.map((tech: string, i: number) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 bg-neuralBlue/20 border border-neuralBlue/30 rounded text-xs text-neuralBlue font-medium"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleApplySuggestion(suggestion)}
                    className="px-3 py-1.5 bg-forgePurple/20 border border-forgePurple/30 hover:bg-forgePurple/30 rounded-lg text-xs font-bold text-forgePurple transition-all opacity-0 group-hover:opacity-100"
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && suggestions.length === 0 && !error && (
          <div className="text-center py-12">
            <Wand2 className="w-16 h-16 mx-auto mb-4 text-techGray/30" />
            <p className="text-sm text-techGray/60 font-medium">
              Click "Generate" to get AI suggestions
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
