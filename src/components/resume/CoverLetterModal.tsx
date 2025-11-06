import { useState } from 'react';
import { X, FileText, Sparkles, Copy, Download, Check, Loader } from 'lucide-react';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

interface CoverLetterModalProps {
  resumeId: number;
  isOpen: boolean;
  onClose: () => void;
}

export default function CoverLetterModal({ resumeId, isOpen, onClose }: CoverLetterModalProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState<'professional' | 'enthusiastic' | 'formal'>('professional');
  const [generatedLetter, setGeneratedLetter] = useState<string | null>(null);
  const [subjectLine, setSubjectLine] = useState<string | null>(null);
  const [variations, setVariations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!jobTitle || !companyName) {
      setError('Please fill in job title and company name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1x/cover-letters/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          resume_id: resumeId,
          job_title: jobTitle,
          company_name: companyName,
          job_description: jobDescription || undefined,
          tone: tone
        })
      });

      if (!response.ok) throw new Error('Failed to generate cover letter');

      const data = await response.json();
      setGeneratedLetter(data.content);
      setSubjectLine(data.subject_line);
      setVariations(data.variations || []);
    } catch (err) {
      console.error('Error generating cover letter:', err);
      setError('Failed to generate cover letter. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!generatedLetter) return;
    
    await navigator.clipboard.writeText(generatedLetter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!generatedLetter) return;

    const blob = new Blob([generatedLetter], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cover-letter-${companyName.replace(/\s+/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-gray-200 animate-scale-in">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600 px-6 py-5 flex items-center justify-between z-10 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center shadow-glass">
              <FileText className="w-7 h-7 text-white drop-shadow-lg" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight drop-shadow-md">AI Cover Letter Generator</h2>
              <p className="text-sm text-white/90 font-medium">Create tailored cover letters in seconds</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-white/80 hover:text-white transition-all duration-200 hover:bg-white/20 rounded-lg p-2"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-88px)]">
          <div className="p-6">
            {error && (
              <div className="mb-4 p-4 bg-gradient-to-r from-red-50 to-red-100 border-l-4 border-red-500 rounded-xl text-red-800 shadow-sm animate-slide-down">
                <p className="font-semibold">{error}</p>
              </div>
            )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Section */}
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
                Job Details
              </h3>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wide">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g., Senior Software Engineer"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 font-medium text-gray-900"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wide">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g., Google"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 font-medium text-gray-900"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wide">
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value as 'professional' | 'enthusiastic' | 'formal')}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 font-medium text-gray-900"
                  >
                    <option value="professional">Professional</option>
                    <option value="enthusiastic">Enthusiastic</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wide">
                    Job Description (Optional)
                  </label>
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description here for better tailoring..."
                    rows={6}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 resize-none font-medium text-gray-900"
                  />
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={loading || !jobTitle || !companyName}
                  className="w-full bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600 hover:from-purple-700 hover:via-pink-700 hover:to-rose-700 text-white font-bold py-4 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader className="w-5 h-5 animate-spin" />
                      Generating Your Cover Letter...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <Sparkles className="w-5 h-5" />
                      Generate Cover Letter
                    </span>
                  )}
                </Button>
              </div>
            </div>

            {/* Output Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Letter</h3>
              
              {!generatedLetter ? (
                <div className="bg-gray-50 rounded-lg p-8 text-center h-full flex flex-col items-center justify-center">
                  <FileText className="w-16 h-16 text-gray-300 mb-4" />
                  <p className="text-gray-600">
                    Fill in the job details and click generate to create your cover letter
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Subject Line */}
                  {subjectLine && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <p className="text-xs font-medium text-blue-900 mb-1">Email Subject:</p>
                      <p className="text-sm text-blue-800">{subjectLine}</p>
                    </div>
                  )}

                  {/* Cover Letter Content */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4 min-h-[400px]">
                    <div className="prose prose-sm max-w-none">
                      {generatedLetter.split('\n').map((paragraph, idx) => (
                        <p key={idx} className="mb-3 text-gray-800 leading-relaxed">
                          {paragraph}
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <Button
                      onClick={handleCopy}
                      variant="outline"
                      className="flex-1"
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                    <Button
                      onClick={handleDownload}
                      variant="outline"
                      className="flex-1"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  </div>

                  {/* Variations */}
                  {variations.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Alternative Versions</h4>
                      <div className="space-y-3">
                        {variations.map((variation, idx) => (
                          <details key={idx} className="bg-gray-50 rounded-lg">
                            <summary className="px-4 py-3 cursor-pointer text-sm font-medium text-gray-700 hover:bg-gray-100">
                              Variation {idx + 1}
                            </summary>
                            <div className="px-4 pb-3 text-sm text-gray-600 leading-relaxed">
                              {variation.split('\n').map((p, pidx) => (
                                <p key={pidx} className="mb-2">{p}</p>
                              ))}
                            </div>
                          </details>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
