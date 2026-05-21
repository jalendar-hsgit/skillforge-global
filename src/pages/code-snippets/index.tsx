import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '@/components/Layout';
import { Search, Code, Copy, Check, ThumbsUp, Filter, ExternalLink } from 'lucide-react';

interface CodeSnippet {
  id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  language: string;
  tags: string[] | null;
  complexity: string | null;
  uses_count: number;
  helpful_count: number;
}

interface SnippetDetail extends CodeSnippet {
  code: string;
  explanation: string | null;
  is_community: boolean;
}

const CATEGORIES = [
  { id: 'all', label: 'All Categories', emoji: '📚' },
  { id: 'sorting', label: 'Sorting', emoji: '📊' },
  { id: 'searching', label: 'Searching', emoji: '🔍' },
  { id: 'strings', label: 'Strings', emoji: '📝' },
  { id: 'arrays', label: 'Arrays', emoji: '📋' },
  { id: 'trees', label: 'Trees', emoji: '🌳' },
  { id: 'graphs', label: 'Graphs', emoji: '🕸️' },
  { id: 'dynamic-programming', label: 'Dynamic Programming', emoji: '🧩' },
  { id: 'math', label: 'Math', emoji: '🔢' },
];

const LANGUAGES = [
  { id: 'all', label: 'All Languages' },
  { id: 'python', label: 'Python' },
  { id: 'javascript', label: 'JavaScript' },
  { id: 'typescript', label: 'TypeScript' },
  { id: 'java', label: 'Java' },
  { id: 'cpp', label: 'C++' },
];

export default function CodeSnippetsPage() {
  const [snippets, setSnippets] = useState<CodeSnippet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  
  // Snippet detail modal
  const [selectedSnippet, setSelectedSnippet] = useState<SnippetDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState<number | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

  useEffect(() => {
    fetchSnippets();
  }, [selectedCategory, selectedLanguage]);

  const fetchSnippets = async () => {
    setLoading(true);
    setError('');
    try {
      let url = `${apiBase}/api/v1x/code-snippets?`;
      if (selectedCategory !== 'all') {
        url += `category=${encodeURIComponent(selectedCategory)}&`;
      }
      if (selectedLanguage !== 'all') {
        url += `language=${encodeURIComponent(selectedLanguage)}&`;
      }
      if (searchQuery) {
        url += `search=${encodeURIComponent(searchQuery)}&`;
      }
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch snippets');
      const data = await response.json();
      setSnippets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading snippets');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSnippets();
  };

  const viewSnippet = async (slug: string) => {
    setLoadingDetail(true);
    try {
      const response = await fetch(`${apiBase}/api/v1x/code-snippets/${slug}`);
      if (!response.ok) throw new Error('Failed to fetch snippet');
      const data = await response.json();
      setSelectedSnippet(data);
    } catch (err) {
      console.error('Error loading snippet:', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const copySnippet = async (slug: string) => {
    try {
      const response = await fetch(`${apiBase}/api/v1x/code-snippets/${slug}/copy`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        await navigator.clipboard.writeText(data.code);
        
        // Find snippet id for visual feedback
        const snippet = snippets.find(s => s.slug === slug) || selectedSnippet;
        if (snippet) {
          setCopiedSnippet(snippet.id);
          setTimeout(() => setCopiedSnippet(null), 2000);
        }
      }
    } catch (err) {
      console.error('Error copying snippet:', err);
    }
  };

  const closeModal = () => {
    setSelectedSnippet(null);
  };

  return (
    <Layout>
      <Head>
        <title>Code Snippets Library - SkillForge</title>
        <meta name="description" content="Reusable code patterns and solutions for common problems" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech">
        {/* Header */}
        <div className="bg-gradient-to-r from-forgePurple via-neuralBlue to-aiElectric py-12">
          <div className="container">
            <div className="flex items-center gap-4 mb-4">
              <Code className="w-10 h-10 text-white" />
              <h1 className="text-4xl font-display font-black text-white">Code Snippets Library</h1>
            </div>
            <p className="text-white/90 text-lg max-w-2xl">
              Reusable code patterns, algorithms, and solutions for common programming problems. 
              Copy, learn, and adapt these snippets for your projects.
            </p>
          </div>
        </div>

        <div className="container py-8">
          {/* Search and Filters */}
          <div className="bg-deepTech-800 rounded-2xl p-6 mb-8 shadow-glow border border-techGray-800">
            <form onSubmit={handleSearch} className="mb-6">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-techGray-400 w-5 h-5" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search snippets (e.g., 'binary search', 'quicksort')..."
                    className="w-full pl-12 pr-4 py-3 bg-deepTech-900 border-2 border-techGray-700 rounded-xl text-white placeholder-techGray-500 focus:border-forgePurple focus:outline-none transition-colors"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3 bg-forgePurple text-white font-semibold rounded-xl hover:bg-forgePurple/90 transition-colors"
                >
                  Search
                </button>
              </div>
            </form>

            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-techGray-400" />
                <span className="text-techGray-300 font-medium">Filters:</span>
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 bg-deepTech-900 border-2 border-techGray-700 rounded-lg text-white focus:border-forgePurple focus:outline-none"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.emoji} {cat.label}
                  </option>
                ))}
              </select>

              {/* Language Filter */}
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="px-4 py-2 bg-deepTech-900 border-2 border-techGray-700 rounded-lg text-white focus:border-forgePurple focus:outline-none"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.id} value={lang.id}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-6 py-4 rounded-xl mb-8">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-forgePurple border-t-transparent"></div>
              <p className="mt-4 text-techGray-400">Loading snippets...</p>
            </div>
          ) : snippets.length === 0 ? (
            <div className="text-center py-16">
              <Code className="w-16 h-16 text-techGray-600 mx-auto mb-4" />
              <p className="text-techGray-400 text-lg">No snippets found matching your criteria.</p>
              <p className="text-techGray-500 mt-2">Try adjusting your filters or search query.</p>
            </div>
          ) : (
            /* Snippets Grid */
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {snippets.map((snippet) => (
                <div
                  key={snippet.id}
                  className="bg-deepTech-800 rounded-2xl p-6 border border-techGray-800 hover:border-forgePurple transition-all duration-300 group cursor-pointer"
                  onClick={() => viewSnippet(snippet.slug)}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-white group-hover:text-forgePurple transition-colors">
                        {snippet.title}
                      </h3>
                      <p className="text-techGray-400 text-sm mt-1 line-clamp-2">
                        {snippet.description}
                      </p>
                    </div>
                    <span className="px-2 py-1 bg-neuralBlue/20 text-neuralBlue text-xs font-mono rounded">
                      {snippet.language}
                    </span>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-2 py-1 bg-forgePurple/20 text-forgePurple text-xs rounded">
                      {snippet.category}
                    </span>
                    {snippet.complexity && (
                      <span className="px-2 py-1 bg-aiElectric/20 text-aiElectric text-xs rounded">
                        {snippet.complexity}
                      </span>
                    )}
                    {snippet.tags?.slice(0, 2).map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-deepTech-700 text-techGray-400 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between pt-4 border-t border-techGray-700">
                    <div className="flex items-center gap-4 text-sm text-techGray-500">
                      <span className="flex items-center gap-1">
                        <Copy className="w-4 h-4" />
                        {snippet.uses_count}
                      </span>
                      <span className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        {snippet.helpful_count}
                      </span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copySnippet(snippet.slug);
                      }}
                      className="flex items-center gap-2 px-3 py-1.5 bg-forgePurple/20 text-forgePurple rounded-lg hover:bg-forgePurple hover:text-white transition-colors"
                    >
                      {copiedSnippet === snippet.id ? (
                        <>
                          <Check className="w-4 h-4" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Snippet Detail Modal */}
        {selectedSnippet && (
          <div 
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <div 
              className="bg-deepTech-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-techGray-700"
              onClick={(e) => e.stopPropagation()}
            >
              {loadingDetail ? (
                <div className="p-12 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-forgePurple border-t-transparent mx-auto"></div>
                </div>
              ) : (
                <>
                  {/* Modal Header */}
                  <div className="p-6 border-b border-techGray-700">
                    <div className="flex items-start justify-between">
                      <div>
                        <h2 className="text-2xl font-bold text-white">{selectedSnippet.title}</h2>
                        <p className="text-techGray-400 mt-2">{selectedSnippet.description}</p>
                      </div>
                      <button
                        onClick={closeModal}
                        className="text-techGray-400 hover:text-white text-2xl"
                      >
                        ×
                      </button>
                    </div>

                    {/* Meta info */}
                    <div className="flex flex-wrap gap-2 mt-4">
                      <span className="px-3 py-1 bg-neuralBlue/20 text-neuralBlue text-sm font-mono rounded">
                        {selectedSnippet.language}
                      </span>
                      <span className="px-3 py-1 bg-forgePurple/20 text-forgePurple text-sm rounded">
                        {selectedSnippet.category}
                      </span>
                      {selectedSnippet.complexity && (
                        <span className="px-3 py-1 bg-aiElectric/20 text-aiElectric text-sm rounded">
                          Complexity: {selectedSnippet.complexity}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Code Block */}
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-techGray-300 font-medium">Code</span>
                      <button
                        onClick={() => copySnippet(selectedSnippet.slug)}
                        className="flex items-center gap-2 px-4 py-2 bg-forgePurple text-white rounded-lg hover:bg-forgePurple/90 transition-colors"
                      >
                        {copiedSnippet === selectedSnippet.id ? (
                          <>
                            <Check className="w-4 h-4" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            Copy Code
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="bg-deepTech-900 p-4 rounded-xl overflow-x-auto border border-techGray-700">
                      <code className="text-sm text-techGray-100 font-mono whitespace-pre">
                        {selectedSnippet.code}
                      </code>
                    </pre>

                    {/* Explanation */}
                    {selectedSnippet.explanation && (
                      <div className="mt-6">
                        <h3 className="text-techGray-300 font-medium mb-3">Explanation</h3>
                        <p className="text-techGray-400 leading-relaxed whitespace-pre-wrap">
                          {selectedSnippet.explanation}
                        </p>
                      </div>
                    )}

                    {/* Tags */}
                    {selectedSnippet.tags && selectedSnippet.tags.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-techGray-300 font-medium mb-3">Tags</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedSnippet.tags.map((tag) => (
                            <span
                              key={tag}
                              className="px-3 py-1 bg-deepTech-700 text-techGray-300 text-sm rounded-full"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="mt-6 pt-6 border-t border-techGray-700 flex items-center gap-6">
                      <span className="flex items-center gap-2 text-techGray-400">
                        <Copy className="w-5 h-5" />
                        {selectedSnippet.uses_count} uses
                      </span>
                      <span className="flex items-center gap-2 text-techGray-400">
                        <ThumbsUp className="w-5 h-5" />
                        {selectedSnippet.helpful_count} found helpful
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
