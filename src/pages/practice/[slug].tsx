import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { 
  Code, Play, RotateCcw, CheckCircle, XCircle, Lightbulb, 
  Trophy, Clock, Target, Zap, ChevronRight, Terminal, 
  Eye, EyeOff, Download, Share2, BookOpen, Layers
} from 'lucide-react'
import Link from 'next/link'
import type { GetServerSideProps } from 'next'
import { useRouter } from 'next/router'
import CodeEditor from '@/components/CodeEditor'

type Challenge = {
  id: number
  slug: string
  title: string
  description: string
  difficulty: string
  category: string
  points: number
  time_limit: number
  starter_code: string
  solution: string
  test_cases: any
  hints: string[]
  is_premium: boolean
  success_rate: number
  supported_languages: string[]
}

type TestResult = {
  test_case: string
  passed: boolean
  expected: any
  actual: any
  execution_time: number
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const base = `http://${ctx.req.headers.host}`
  const r = await fetch(`${base}/api/session/me`, {
    headers: { cookie: ctx.req.headers.cookie || '' }
  })
  if (!r.ok) {
    return { redirect: { destination: '/login', permanent: false } }
  }
  return { props: {} }
}

const difficultyColors = {
  beginner: 'bg-green-500/20 text-green-400 border-green-500/30',
  easy: 'bg-green-500/20 text-green-400 border-green-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  hard: 'bg-red-500/20 text-red-400 border-red-500/30',
  expert: 'bg-purple-500/20 text-purple-400 border-purple-500/30'
}

const languageTemplates = {
  python: '# Write your solution here\ndef solution():\n    pass\n',
  javascript: '// Write your solution here\nfunction solution() {\n    \n}\n',
  typescript: '// Write your solution here\nfunction solution(): void {\n    \n}\n',
  java: '// Write your solution here\npublic class Solution {\n    public void solution() {\n        \n    }\n}\n',
  cpp: '// Write your solution here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}\n',
  go: '// Write your solution here\npackage main\n\nimport "fmt"\n\nfunc main() {\n    \n}\n',
  rust: '// Write your solution here\nfn main() {\n    \n}\n',
  sql: '-- Write your SQL query here\nSELECT * FROM table_name;\n'
}

export default function ChallengeDetail() {
  const router = useRouter()
  const { slug } = router.query
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [code, setCode] = useState<string>('')
  const [language, setLanguage] = useState<string>('python')
  const [output, setOutput] = useState<string>('')
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [showHints, setShowHints] = useState(false)
  const [showSolution, setShowSolution] = useState(false)
  const [activeTab, setActiveTab] = useState<'description' | 'hints' | 'discussion'>('description')
  const [loading, setLoading] = useState(true)
  const [executionTime, setExecutionTime] = useState<number>(0)
  const [passedTests, setPassedTests] = useState<number>(0)
  const [unlockedHints, setUnlockedHints] = useState<number[]>([])
  const [userCoins, setUserCoins] = useState<number>(100) // Mock user coins

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

  useEffect(() => {
    if (slug) {
      fetchChallenge()
      fetchUserProgress()
    }
  }, [slug])

  const fetchUserProgress = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/my-stats`, {
        credentials: 'include'
      })
      if (res.ok) {
        const data = await res.json()
        setUserCoins(data.total_coins || 100) // Default to 100 if no coins
        
        // Fetch unlocked hints for this challenge from localStorage
        const storedHints = localStorage.getItem(`hints_${slug}`)
        if (storedHints) {
          setUnlockedHints(JSON.parse(storedHints))
        }
      }
    } catch (error) {
      console.error('Failed to fetch user progress:', error)
      // Keep default 100 coins
    }
  }

  const fetchChallenge = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/challenges/${slug}`, {
        credentials: 'include'
      })
      if (res.ok) {
        const data = await res.json()
        setChallenge(data)
        setCode(data.starter_code || languageTemplates[language as keyof typeof languageTemplates])
      }
    } catch (error) {
      console.error('Failed to fetch challenge:', error)
    } finally {
      setLoading(false)
    }
  }

  const unlockHint = async (hintIndex: number, cost: number) => {
    if (userCoins < cost) return
    
    // Update local state
    const newUnlockedHints = [...unlockedHints, hintIndex]
    setUnlockedHints(newUnlockedHints)
    setUserCoins(userCoins - cost)
    
    // Persist to localStorage
    localStorage.setItem(`hints_${slug}`, JSON.stringify(newUnlockedHints))
    
    // Optionally call backend to track hint unlock (TODO: add backend endpoint)
    try {
      await fetch(`${API_BASE}/api/v1x/coding-practice/challenges/${slug}/unlock-hint`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hint_index: hintIndex, cost })
      })
    } catch (error) {
      console.error('Failed to track hint unlock:', error)
      // Continue anyway - local unlock already happened
    }
  }

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang)
    if (challenge?.starter_code) {
      setCode(challenge.starter_code)
    } else {
      setCode(languageTemplates[newLang as keyof typeof languageTemplates])
    }
  }

  const runCode = async () => {
    setIsRunning(true)
    setOutput('')
    setTestResults([])
    
    const startTime = Date.now()
    
    try {
      // Call real code execution API
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          language: language,
          code: code
        })
      })
      
      if (!res.ok) {
        const error = await res.json()
        setOutput(`Error: ${error.detail || 'Failed to run code'}`)
        return
      }
      
      const result = await res.json()
      
      if (result.success) {
        setOutput(`✅ Success!\n\nOutput:\n${result.output}\n\nExecution time: ${result.execution_time.toFixed(2)}ms`)
      } else {
        setOutput(`❌ Error:\n${result.error || 'Unknown error'}\n\nExecution time: ${result.execution_time.toFixed(2)}ms`)
      }
      
      setExecutionTime(Date.now() - startTime)
      
    } catch (error) {
      setOutput(`Error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }

  const submitCode = async () => {
    setIsRunning(true)
    setOutput('')
    setTestResults([])
    
    try {
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/challenges/${challenge?.id}/submit`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_id: challenge?.id,
          code,
          language
        })
      })
      
      if (res.ok) {
        const result = await res.json()
        
        // Show test results if available
        if (result.test_results && result.test_results.length > 0) {
          setTestResults(result.test_results)
          const passed = result.test_results.filter((t: TestResult) => t.passed).length
          const total = result.test_results.length
          setPassedTests(passed)
          
          setOutput(`
✅ Submission Complete!

Score: ${result.score}%
Tests Passed: ${passed}/${total}
Execution Time: ${result.execution_time_ms}ms
Coins Earned: ${result.coins_earned || 0}

${result.score >= 100 ? '🎉 Perfect Score! All test cases passed!' : ''}
          `.trim())
        } else {
          setOutput(`Submission successful!\nScore: ${result.score}%\nCoins earned: ${result.coins_earned || 0}`)
        }
      } else {
        const error = await res.json()
        setOutput(`Submission failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      setOutput(`Submission error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }

  const resetCode = () => {
    if (challenge?.starter_code) {
      setCode(challenge.starter_code)
    } else {
      setCode(languageTemplates[language as keyof typeof languageTemplates])
    }
    setOutput('')
    setTestResults([])
  }

  if (loading) {
    return (
      <Layout maxWidth="full">
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forgePurple"></div>
        </div>
      </Layout>
    )
  }

  if (!challenge) {
    return (
      <Layout maxWidth="7xl">
        <div className="text-center py-12">
          <Code className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Challenge not found</p>
          <Link href="/practice" className="mt-4 inline-block text-forgePurple hover:text-neuralBlue">
            ← Back to Practice
          </Link>
        </div>
      </Layout>
    )
  }

  return (
    <Layout maxWidth="full" className="px-0">
      <Head>
        <title>{challenge.title} – Coding Practice – SkillForge Global</title>
      </Head>

      {/* Header Bar */}
      <div className="sticky top-0 z-40 bg-darkNavy/95 backdrop-blur-sm border-b border-techBlue/20">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/practice" 
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Back
            </Link>
            <div className="h-6 w-px bg-techBlue/30"></div>
            <h1 className="text-xl font-bold text-white">{challenge.title}</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${difficultyColors[challenge.difficulty as keyof typeof difficultyColors]}`}>
              {challenge.difficulty}
            </span>
            {challenge.is_premium && (
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                Premium
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Trophy className="w-4 h-4 text-yellow-400" />
              <span>{challenge.points} points</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Target className="w-4 h-4 text-green-400" />
              <span>{(challenge.success_rate || 0).toFixed(0)}% success</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Split View */}
      <div className="flex" style={{ height: 'calc(100vh - 130px)' }}>
        
        {/* Left Panel - Problem Description */}
        <div className="w-1/3 border-r border-techBlue/20 overflow-y-auto bg-darkNavy/50">
          <div className="p-6">
            
            {/* Tabs */}
            <div className="flex items-center gap-2 mb-6 border-b border-techBlue/20">
              <button
                onClick={() => setActiveTab('description')}
                className={`px-4 py-2 font-medium transition-colors relative ${
                  activeTab === 'description' 
                    ? 'text-forgePurple' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Description
                {activeTab === 'description' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-forgePurple"></div>
                )}
              </button>
              <button
                onClick={() => setActiveTab('hints')}
                className={`px-4 py-2 font-medium transition-colors relative ${
                  activeTab === 'hints' 
                    ? 'text-forgePurple' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <Lightbulb className="w-4 h-4 inline-block mr-1" />
                Hints
                {activeTab === 'hints' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-forgePurple"></div>
                )}
              </button>
              <button
                onClick={() => setActiveTab('discussion')}
                className={`px-4 py-2 font-medium transition-colors relative ${
                  activeTab === 'discussion' 
                    ? 'text-forgePurple' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Discussion
                {activeTab === 'discussion' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-forgePurple"></div>
                )}
              </button>
            </div>

            {/* Description Tab */}
            {activeTab === 'description' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">Problem Statement</h3>
                  <div className="text-gray-300 leading-relaxed">
                    {challenge.description || 'Write a function that solves this coding challenge efficiently.'}
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-forgePurple/10 border border-forgePurple/20">
                  <h4 className="font-semibold text-white mb-2">Example:</h4>
                  <div className="font-mono text-sm text-gray-300 space-y-2">
                    <div>Input: [1, 2, 3, 4, 5]</div>
                    <div>Output: [5, 4, 3, 2, 1]</div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-white mb-3">Constraints:</h4>
                  <ul className="space-y-2 text-gray-300 text-sm">
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 mt-0.5 text-forgePurple flex-shrink-0" />
                      Time limit: {challenge.time_limit || 5}s
                    </li>
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 mt-0.5 text-forgePurple flex-shrink-0" />
                      Memory limit: 256 MB
                    </li>
                    <li className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 mt-0.5 text-forgePurple flex-shrink-0" />
                      1 ≤ n ≤ 10^5
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-white mb-3">Tags:</h4>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-techBlue/20 text-techBlue border border-techBlue/30">
                      {challenge.category.replace('_', ' ')}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-neuralBlue/20 text-neuralBlue border border-neuralBlue/30">
                      Arrays
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-forgePurple/20 text-forgePurple border border-forgePurple/30">
                      Two Pointers
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Hints Tab */}
            {activeTab === 'hints' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    <span className="text-sm text-gray-300">
                      {unlockedHints.length} of {(challenge.hints || []).length || 3} hints unlocked
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-yellow-400">
                    <Trophy className="w-4 h-4" />
                    <span className="text-sm font-medium">{userCoins} coins</span>
                  </div>
                </div>

                {(challenge.hints || ['Think about edge cases first', 'Consider using a hash map for O(1) lookups', 'Try the two-pointer technique']).map((hint, idx) => {
                  const isUnlocked = unlockedHints.includes(idx)
                  const hintCost = (idx + 1) * 5
                  
                  return (
                    <div 
                      key={idx}
                      className={`p-4 rounded-lg border ${
                        isUnlocked 
                          ? 'bg-yellow-500/10 border-yellow-500/20' 
                          : 'bg-gray-800/50 border-gray-700/30'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          isUnlocked ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700 text-gray-500'
                        }`}>
                          {isUnlocked ? <Lightbulb className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">Hint {idx + 1}</span>
                            {!isUnlocked && (
                              <button
                                onClick={() => unlockHint(idx, hintCost)}
                                disabled={userCoins < hintCost}
                                className="px-3 py-1 rounded-lg bg-yellow-500/20 text-yellow-400 text-xs font-medium hover:bg-yellow-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                              >
                                <Trophy className="w-3 h-3" />
                                Unlock ({hintCost} coins)
                              </button>
                            )}
                          </div>
                          {isUnlocked ? (
                            <p className="text-gray-300 text-sm leading-relaxed">{hint}</p>
                          ) : (
                            <p className="text-gray-500 text-sm italic">🔒 Unlock this hint to reveal it</p>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}

                {unlockedHints.length === (challenge.hints || []).length && (challenge.hints || []).length > 0 && (
                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-center">
                    <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <p className="text-green-400 font-medium">All hints unlocked! 🎉</p>
                    <p className="text-sm text-gray-400 mt-1">You've got all the clues you need</p>
                  </div>
                )}
                
                {!showSolution ? (
                  <button
                    onClick={() => setShowSolution(true)}
                    className="w-full py-3 px-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-colors font-medium"
                  >
                    <Eye className="w-4 h-4 inline-block mr-2" />
                    Reveal Solution (Costs 50 coins)
                  </button>
                ) : (
                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <div className="font-semibold text-white mb-2">Solution Approach</div>
                        <div className="text-gray-300 text-sm space-y-2">
                          <p>Use a two-pointer approach to solve this efficiently in O(n) time complexity.</p>
                          <div className="mt-3 p-3 rounded bg-darkNavy font-mono text-xs text-green-400">
                            {challenge.solution || '# Solution code here'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Discussion Tab */}
            {activeTab === 'discussion' && (
              <div className="space-y-4">
                <div className="text-center py-12">
                  <BookOpen className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">No discussions yet. Be the first to share!</p>
                  <button className="mt-4 px-4 py-2 rounded-lg bg-forgePurple/20 text-forgePurple border border-forgePurple/30 hover:bg-forgePurple/30 transition-colors">
                    Start Discussion
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Code Editor & Output */}
        <div className="flex-1 flex flex-col">
          
          {/* Editor Toolbar */}
          <div className="flex items-center justify-between px-6 py-3 bg-darkNavy/80 border-b border-techBlue/20">
            <div className="flex items-center gap-3">
              <Code className="w-5 h-5 text-forgePurple" />
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-darkNavy border border-techBlue/30 text-white text-sm focus:outline-none focus:border-techBlue"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="sql">SQL</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={resetCode}
                className="px-3 py-1.5 rounded-lg bg-gray-600/20 text-gray-300 hover:bg-gray-600/30 transition-colors text-sm font-medium flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
              <button
                onClick={runCode}
                disabled={isRunning}
                className="px-4 py-1.5 rounded-lg bg-green-600/20 text-green-400 hover:bg-green-600/30 transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                {isRunning ? 'Running...' : 'Run Code'}
              </button>
              <button
                onClick={submitCode}
                disabled={isRunning}
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue text-white hover:shadow-lg hover:shadow-forgePurple/50 transition-all text-sm font-medium flex items-center gap-2 disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                Submit
              </button>
            </div>
          </div>

          {/* Code Editor */}
          <div className="flex-1 overflow-hidden">
            <CodeEditor
              value={code}
              onChange={setCode}
              language={language}
              height="100%"
            />
          </div>

          {/* Output Panel */}
          <div className="h-64 border-t border-techBlue/20 bg-darkNavy/90">
            <div className="px-6 py-3 border-b border-techBlue/20 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Terminal className="w-5 h-5 text-forgePurple" />
                <span className="font-semibold text-white">Output</span>
                {executionTime > 0 && (
                  <span className="text-sm text-gray-400">
                    ({executionTime}ms)
                  </span>
                )}
              </div>
              {testResults.length > 0 && (
                <div className="text-sm">
                  <span className={passedTests === testResults.length ? 'text-green-400' : 'text-yellow-400'}>
                    {passedTests}/{testResults.length} tests passed
                  </span>
                </div>
              )}
            </div>
            
            <div className="p-6 overflow-y-auto h-[calc(100%-52px)]">
              {testResults.length > 0 ? (
                <div className="space-y-3">
                  {testResults.map((result, idx) => (
                    <div 
                      key={idx}
                      className={`p-3 rounded-lg border ${
                        result.passed 
                          ? 'bg-green-500/10 border-green-500/30' 
                          : 'bg-red-500/10 border-red-500/30'
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        {result.passed ? (
                          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <div className="font-medium text-white text-sm">{result.test_case}</div>
                          {!result.passed && (
                            <div className="mt-2 text-xs space-y-1">
                              <div className="text-gray-400">Expected: <span className="text-green-400">{result.expected}</span></div>
                              <div className="text-gray-400">Actual: <span className="text-red-400">{result.actual}</span></div>
                            </div>
                          )}
                          <div className="text-xs text-gray-500 mt-1">{result.execution_time}s</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : output ? (
                <pre className="font-mono text-sm text-gray-300 whitespace-pre-wrap">{output}</pre>
              ) : (
                <div className="text-gray-500 text-sm">
                  Click "Run Code" to test your solution or "Submit" to submit for grading.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
