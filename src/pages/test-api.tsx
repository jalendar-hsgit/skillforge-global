import { useState, useEffect } from 'react';

export default function TestAPI() {
  const [results, setResults] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testEndpoint = async (url: string, label: string) => {
    try {
      setResults(prev => prev + `\n\n[${label}]\nTesting: ${url}`);
      const response = await fetch(url, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const text = await response.text();
      setResults(prev => prev + `\nStatus: ${response.status}\nResponse: ${text.substring(0, 200)}`);
    } catch (err: any) {
      setResults(prev => prev + `\nError: ${err.message}`);
    }
  };

  const runTests = async () => {
    setLoading(true);
    setResults('Starting tests...');
    
    // Test 1: Direct backend
    await testEndpoint('http://localhost:8001/api/v1x/mentors/sessions/my', 'Direct Backend');
    
    // Test 2: Through proxy
    await testEndpoint('/api/session/v1x/mentors/sessions/my', 'Through Proxy');
    
    // Test 3: Check auth
    await testEndpoint('/api/session/me', 'Check Auth (Proxy)');
    
    setLoading(false);
  };

  useEffect(() => {
    // Auto-run on mount
    runTests();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
      <h1>API Testing Page</h1>
      <button onClick={runTests} disabled={loading}>
        {loading ? 'Testing...' : 'Run Tests'}
      </button>
      <hr />
      <pre>{results}</pre>
    </div>
  );
}
