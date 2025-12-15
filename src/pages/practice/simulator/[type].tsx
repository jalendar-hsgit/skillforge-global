import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'
import { Code, Play, RotateCcw, Terminal, CheckCircle, XCircle, Download, Copy, Maximize2, Minimize2 } from 'lucide-react'
import Link from 'next/link'
import type { GetServerSideProps } from 'next'
import CodeEditor from '@/components/CodeEditor'

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

const simulators = [
  {
    id: 'code-editor',
    name: 'Code Editor',
    description: 'Multi-language IDE with syntax highlighting and execution',
    languages: ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'Rust'],
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'terminal',
    name: 'Terminal',
    description: 'Linux/Bash command line practice environment',
    languages: ['Bash', 'Shell', 'Linux'],
    color: 'from-green-500 to-teal-500'
  },
  {
    id: 'database',
    name: 'SQL Playground',
    description: 'Practice SQL queries with live database',
    languages: ['MySQL', 'PostgreSQL', 'SQLite'],
    color: 'from-blue-500 to-indigo-500'
  },
  {
    id: 'cloud-console',
    name: 'Cloud Console',
    description: 'AWS/Azure CLI practice environment',
    languages: ['AWS CLI', 'Azure CLI', 'GCloud'],
    color: 'from-orange-500 to-red-500'
  },
  {
    id: 'kubernetes',
    name: 'Kubernetes Cluster',
    description: 'Deploy and manage K8s resources',
    languages: ['kubectl', 'helm', 'YAML'],
    color: 'from-cyan-500 to-blue-500'
  },
  {
    id: 'docker',
    name: 'Docker Lab',
    description: 'Container management and orchestration',
    languages: ['Docker', 'Dockerfile', 'Compose'],
    color: 'from-blue-600 to-sky-500'
  },
  {
    id: 'api-playground',
    name: 'API Playground',
    description: 'Test REST APIs and GraphQL queries',
    languages: ['REST', 'GraphQL', 'JSON'],
    color: 'from-pink-500 to-rose-500'
  },
  {
    id: 'web-editor',
    name: 'Web Editor',
    description: 'HTML/CSS/JS with live preview',
    languages: ['HTML', 'CSS', 'JavaScript'],
    color: 'from-yellow-500 to-amber-500'
  }
]

export default function SimulatorPage() {
  const [selectedSimulator, setSelectedSimulator] = useState(simulators[0])
  const [code, setCode] = useState('')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  useEffect(() => {
    // Set default code based on simulator
    const defaultCode = getDefaultCode(selectedSimulator.id)
    setCode(defaultCode)
  }, [selectedSimulator])

  const getDefaultCode = (simulatorId: string): string => {
    const templates: Record<string, string> = {
      'code-editor': '# Python Code Editor\nprint("Hello, World!")\n\n# Try writing your own code:\ndef greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("Coder"))',
      'terminal': '# Linux Terminal Simulator\n# Try commands like:\nls -la\npwd\necho "Hello from terminal"\ncat /etc/os-release',
      'database': '-- SQL Playground\n-- Sample database: employees\nSELECT * FROM employees\nWHERE department = \'Engineering\'\nLIMIT 10;',
      'cloud-console': '# AWS CLI Simulator\n# Try AWS commands:\naws s3 ls\naws ec2 describe-instances\naws lambda list-functions',
      'kubernetes': '# Kubernetes Cluster\n# Try kubectl commands:\nkubectl get pods\nkubectl get services\nkubectl describe deployment my-app',
      'docker': '# Docker Lab\n# Try Docker commands:\ndocker ps\ndocker images\ndocker run -d nginx\ndocker-compose up',
      'api-playground': '// API Playground\n// Test REST API endpoint:\nGET https://api.example.com/users\n\n// Headers:\n{\n  "Authorization": "Bearer token",\n  "Content-Type": "application/json"\n}',
      'web-editor': '<!DOCTYPE html>\n<html>\n<head>\n  <style>\n    body { font-family: Arial; padding: 20px; }\n    h1 { color: #7c3aed; }\n  </style>\n</head>\n<body>\n  <h1>Hello World!</h1>\n  <p>Edit this code and see live preview!</p>\n  <script>\n    console.log("JavaScript works!");\n  </script>\n</body>\n</html>'
    }
    return templates[simulatorId] || '// Write your code here'
  }

  const runCode = async () => {
    setIsRunning(true)
    setOutput('Running code...')
    
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
      const res = await fetch(`${API_BASE}/api/v1x/coding-practice/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          language: 'python',
          code: code
        })
      })
      
      if (!res.ok) {
        const error = await res.json()
        setOutput(`❌ Error: ${error.detail || 'Failed to run code'}`)
        return
      }
      
      const result = await res.json()
      
      if (result.success) {
        setOutput(`✅ Success!\n\nOutput:\n${result.output}\n\nExecution time: ${result.execution_time.toFixed(2)}ms`)
      } else {
        setOutput(`❌ Error:\n${result.error || 'Unknown error'}\n\nExecution time: ${result.execution_time.toFixed(2)}ms`)
      }
    } catch (error) {
      setOutput(`❌ Error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }

  const resetCode = () => {
    setCode(getDefaultCode(selectedSimulator.id))
    setOutput('')
  }

  const copyCode = () => {
    navigator.clipboard.writeText(code)
    // Could add a toast notification here
  }

  return (
    <Layout maxWidth="full">
      <Head>
        <title>Code Simulators – SkillForge Global</title>
      </Head>

      {/* Header */}
      <div className="sticky top-0 z-40 bg-darkNavy/95 backdrop-blur-sm border-b border-techBlue/20">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/practice" className="text-gray-400 hover:text-white transition-colors">
              ← Back to Practice
            </Link>
            <div className="h-6 w-px bg-techBlue/30"></div>
            <h1 className="text-xl font-bold text-white">Code Simulators</h1>
          </div>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 rounded-lg bg-darkNavy border border-techBlue/30 text-gray-400 hover:text-white transition-colors"
          >
            {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      <div className="flex" style={{ height: 'calc(100vh - 130px)' }}>
        
        {/* Left Sidebar - Simulator Selection */}
        {!isFullscreen && (
          <div className="w-64 border-r border-techBlue/20 bg-darkNavy/50 overflow-y-auto">
            <div className="p-4">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
                Select Simulator
              </h2>
              <div className="space-y-2">
                {simulators.map((sim) => (
                  <button
                    key={sim.id}
                    onClick={() => setSelectedSimulator(sim)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      selectedSimulator.id === sim.id
                        ? 'bg-gradient-to-r ' + sim.color + ' text-white'
                        : 'bg-darkNavy border border-techBlue/20 text-gray-300 hover:border-techBlue/40'
                    }`}
                  >
                    <div className="font-medium text-sm mb-1">{sim.name}</div>
                    <div className="text-xs opacity-80">{sim.languages.slice(0, 2).join(', ')}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Main Simulator Area */}
        <div className="flex-1 flex flex-col">
          
          {/* Simulator Info Banner */}
          <div className={`px-6 py-4 bg-gradient-to-r ${selectedSimulator.color} bg-opacity-10 border-b border-techBlue/20`}>
            <h2 className="text-xl font-bold text-white mb-1">{selectedSimulator.name}</h2>
            <p className="text-sm text-gray-300">{selectedSimulator.description}</p>
            <div className="flex gap-2 mt-3">
              {selectedSimulator.languages.map((lang) => (
                <span 
                  key={lang}
                  className="px-2 py-1 rounded text-xs font-medium bg-white/10 text-white"
                >
                  {lang}
                </span>
              ))}
            </div>
          </div>

          {/* Toolbar */}
          <div className="flex items-center justify-between px-6 py-3 bg-darkNavy/80 border-b border-techBlue/20">
            <div className="flex items-center gap-2">
              <Terminal className="w-5 h-5 text-forgePurple" />
              <span className="text-sm font-medium text-gray-300">Interactive Editor</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={copyCode}
                className="px-3 py-1.5 rounded-lg bg-gray-600/20 text-gray-300 hover:bg-gray-600/30 transition-colors text-sm font-medium flex items-center gap-2"
              >
                <Copy className="w-4 h-4" />
                Copy
              </button>
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
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-forgePurple to-neuralBlue text-white hover:shadow-lg hover:shadow-forgePurple/50 transition-all text-sm font-medium flex items-center gap-2 disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                {isRunning ? 'Running...' : 'Run Code'}
              </button>
            </div>
          </div>

          {/* Split Editor and Output */}
          <div className="flex-1 flex">
            
            {/* Code Editor */}
            <div className="flex-1 overflow-hidden border-r border-techBlue/20">
              <div className="px-4 py-2 bg-darkNavy/80 border-b border-techBlue/20">
                <span className="text-xs font-medium text-gray-400">EDITOR</span>
              </div>
              <CodeEditor
                value={code}
                onChange={setCode}
                language="python"
                height="calc(100% - 36px)"
              />
            </div>

            {/* Output Panel */}
            <div className="w-1/2 bg-darkNavy/90 overflow-hidden">
              <div className="px-4 py-2 bg-darkNavy/80 border-b border-techBlue/20 flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">OUTPUT</span>
                {output && (
                  <Download className="w-4 h-4 text-gray-400 cursor-pointer hover:text-white transition-colors" />
                )}
              </div>
              <div className="p-6 overflow-y-auto h-[calc(100%-36px)]">
                {output ? (
                  <pre className="font-mono text-sm text-gray-300 whitespace-pre-wrap">{output}</pre>
                ) : (
                  <div className="text-center py-12">
                    <Terminal className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-500 text-sm">
                      Click "Run Code" to see output
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Tips Bar */}
      <div className="border-t border-techBlue/20 bg-darkNavy/80 px-6 py-2">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center gap-4">
            <span>💡 Tip: Press Ctrl+Enter to run code</span>
            <span>•</span>
            <span>🎯 All simulators run in isolated environments</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span>Connected</span>
          </div>
        </div>
      </div>
    </Layout>
  )
}
