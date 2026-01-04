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
      
      // Extract skills if available
      const skills = resume.skills || [];
      
      const response = await fetch('/api/session/resume-ai/professional-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: resume.title || 'Professional',
          years_of_experience: yearsOfExperience,
          skills: skills.slice(0, 5), // Top 5 skills
          target_role: undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate summary');
      }
      
      const data = await response.json();
      
      // Create suggestions from main summary + variations
      const suggestionsList = [
        {
          type: 'summary',
          content: data.summary,
          confidence: 0.95,
          isMainVersion: true
        },
        ...(data.variations || []).map((variation: string, idx: number) => ({
          type: 'summary',
          content: variation,
          confidence: 0.85 - (idx * 0.05),
          isMainVersion: false
        }))
      ];
      
      setSuggestions(suggestionsList);
    } catch (err: any) {
      setError(err.message || 'Failed to generate summary. Please try again.');
      console.error('Summary generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateBullets = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get all work experiences and generate for each
      const workExperiences = resume.work_experiences || [];
      
      if (workExperiences.length === 0) {
        setError('Add work experience first to generate bullets');
        setLoading(false);
        return;
      }

      // Generate for most recent job first
      const responses = await Promise.all(
        workExperiences.slice(0, 3).map(job =>
          fetch('/api/session/resume-ai/bullets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
              job_title: job.title || 'Professional',
              company: job.company || 'Company',
              description: job.description || '',
            }),
          }).then(r => r.ok ? r.json() : Promise.reject(`Failed to generate for ${job.company}`))
        )
      );
      
      // Flatten all bullets with metadata
      const allBullets = responses.flatMap((data, jobIdx) => 
        (data.bullet_points || []).map((bullet: string, bulletIdx: number) => ({
          type: 'bullet',
          content: bullet,
          company: workExperiences[jobIdx].company,
          jobTitle: workExperiences[jobIdx].title,
          confidence: 0.9 - (bulletIdx * 0.05),
          jobIndex: jobIdx
        }))
      );
      
      setSuggestions(allBullets.slice(0, 15)); // Limit to 15 suggestions
    } catch (err: any) {
      setError(err.message || 'Failed to generate bullets. Please try again.');
      console.error('Bullets generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateKeywords = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use summary, title, and work experience as context
      const summary = resume.summary || resume.title || 'Professional';
      const recentRoles = (resume.work_experiences || [])
        .slice(0, 2)
        .map(w => w.title)
        .join(', ');

      const response = await fetch('/api/session/resume-ai/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          job_description: `${summary}. Recent roles: ${recentRoles || 'Not specified'}`,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate keywords');
      }
      
      const data = await response.json();
      setSuggestions((data.keywords || []).map((keyword: string) => ({ 
        type: 'keyword',
        content: keyword,
        confidence: 0.8
      })));
    } catch (err: any) {
      setError(err.message || 'Failed to generate keywords. Please try again.');
      console.error('Keywords generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      // Determine skill level from experience
      const yearsOfExp = (resume.work_experiences || []).length * 2;
      const skillLevel = yearsOfExp >= 7 ? 'advanced' : yearsOfExp >= 3 ? 'intermediate' : 'beginner';
      
      const response = await fetch('/api/session/resume-ai/project-ideas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          skill_level: skillLevel,
          technologies: (resume.skills || []).slice(0, 3),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate projects');
      }
      
      const data = await response.json();
      setSuggestions((data.projects || []).map((project: any, idx: number) => ({ 
        type: 'project',
        content: project.title,
        description: project.description,
        tech_stack: project.tech_stack || [],
        confidence: 0.85 - (idx * 0.05)
      })));
    } catch (err: any) {
      setError(err.message || 'Failed to generate projects. Please try again.');
      console.error('Projects generation error:', err);
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
    try {
      switch (suggestion.type) {
        case 'summary':
          onApply('professional_summary', suggestion.content);
          break;
        case 'keyword':
          // Add to skills array
          const currentSkills = resume.skills || [];
          const newSkills = Array.from(new Set([...currentSkills, suggestion.content]));
          onApply('skills', newSkills);
          break;
        case 'bullet':
          // Add to the appropriate work experience's bullets
          const workExperiences = resume.work_experiences || [];
          const jobToUpdate = workExperiences[suggestion.jobIndex];
          
          if (jobToUpdate) {
            const updatedJob = {
              ...jobToUpdate,
              description: (jobToUpdate.description || '') + 
                (jobToUpdate.description ? '\n' : '') + 
                suggestion.content
            };
            
            const updatedExperiences = [...workExperiences];
            updatedExperiences[suggestion.jobIndex] = updatedJob;
            onApply('work_experiences', updatedExperiences);
          }
          break;
        case 'project':
          // Add to projects array
          const currentProjects = resume.projects || [];
          const newProject = {
            title: suggestion.content,
            description: suggestion.description || '',
            tech_stack: suggestion.tech_stack || []
          };
          onApply('projects', [...currentProjects, newProject]);
          break;
      }
      
      // Show confirmation
      setError(null);
    } catch (err) {
      console.error('Error applying suggestion:', err);
      setError('Failed to apply suggestion');
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
              {suggestions.length} Suggestion{suggestions.length !== 1 ? 's' : ''} Ready
            </h4>
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 hover:border-white/20 transition-all duration-200 group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    {/* Metadata badges */}
                    {(suggestion.company || suggestion.jobTitle) && (
                      <div className="flex gap-2 mb-2 flex-wrap">
                        {suggestion.company && (
                          <span className="text-xs px-2 py-1 bg-neuralBlue/20 border border-neuralBlue/30 rounded text-neuralBlue font-medium">
                            {suggestion.company}
                          </span>
                        )}
                        {suggestion.jobTitle && (
                          <span className="text-xs px-2 py-1 bg-forgePurple/20 border border-forgePurple/30 rounded text-forgePurple font-medium">
                            {suggestion.jobTitle}
                          </span>
                        )}
                        {suggestion.isMainVersion && (
                          <span className="text-xs px-2 py-1 bg-yellow-500/20 border border-yellow-500/30 rounded text-yellow-400 font-bold">
                            PRIMARY
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Content */}
                    <p className="text-sm text-white font-medium leading-relaxed mb-2">
                      {suggestion.content}
                    </p>
                    
                    {/* Description if available */}
                    {suggestion.description && (
                      <p className="text-xs text-techGray/80 mb-2">
                        {suggestion.description}
                      </p>
                    )}
                    
                    {/* Tech stack if available */}
                    {suggestion.tech_stack && suggestion.tech_stack.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-2">
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
                    
                    {/* Confidence score */}
                    {suggestion.confidence && (
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 flex-1 max-w-[120px] bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue"
                            style={{ width: `${suggestion.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-techGray/60 font-medium">
                          {Math.round(suggestion.confidence * 100)}% match
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Apply Button */}
                  <button
                    onClick={() => handleApplySuggestion(suggestion)}
                    className="px-3 py-1.5 bg-forgePurple/20 border border-forgePurple/30 hover:bg-forgePurple/40 rounded-lg text-xs font-bold text-forgePurple transition-all opacity-0 group-hover:opacity-100"
                    title="Apply this suggestion to your resume"
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
