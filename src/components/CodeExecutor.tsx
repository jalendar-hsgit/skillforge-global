import React, { useState, useRef, useEffect } from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { apiCall } from '@/lib/api';

interface TestCase {
  input_data: string;
  expected_output: string;
  is_sample: boolean;
}

interface ExecutionResult {
  id: number;
  status: string;
  test_cases_total: number;
  test_cases_passed: number;
  test_cases_failed: number;
  execution_time_ms: number | null;
  memory_used_mb: number | null;
  points_earned: number;
  error_message: string | null;
  compilation_log: string | null;
  test_results: Array<{
    test_case_number: number;
    status: string;
    passed: boolean;
    actual_output: string | null;
    expected_output: string;
    input_data: string;
    error_message: string | null;
  }>;
}

interface CodeExecutorProps {
  challengeId?: number;
  contestId?: number;
  testCases?: TestCase[];
  initialCode?: string;
  onSuccess?: (result: ExecutionResult) => void;
}

const CodeExecutor: React.FC<CodeExecutorProps> = ({
  challengeId,
  contestId,
  testCases = [],
  initialCode = '',
  onSuccess,
}) => {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState('python');
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [error, setError] = useState('');
  const codeEditorRef = useRef<HTMLTextAreaElement>(null);

  const languages = [
    { value: 'python', label: 'Python 3' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
  ];

  const handleExecute = async () => {
    if (!code.trim()) {
      setError('Please write some code first');
      return;
    }

    try {
      setExecuting(true);
      setError('');
      setResult(null);

      const response = await apiCall('/api/v1x/execute/run', {
        method: 'POST',
        body: JSON.stringify({
          code,
          language,
          challenge_id: challengeId,
          contest_id: contestId,
          test_cases: testCases,
          time_limit_seconds: 5,
          memory_limit_mb: 256,
        }),
      });

      setResult(response);
      onSuccess?.(response);
    } catch (err: any) {
      setError(err.message || 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'error':
      case 'compilation_error':
        return 'text-red-600';
      case 'timeout':
        return 'text-orange-600';
      case 'running':
      case 'pending':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTestCaseStatusColor = (passed: boolean) => {
    return passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Editor Section */}
      <Card>
        <h2 className="text-2xl font-bold mb-4">💻 Code Editor</h2>

        {/* Language Selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={executing}
            className="w-full md:w-48 px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        {/* Code Editor */}
        <textarea
          ref={codeEditorRef}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          disabled={executing}
          placeholder="Write your code here..."
          className="w-full h-64 p-4 border border-gray-300 rounded-lg font-mono text-sm disabled:opacity-50 disabled:bg-gray-50"
        />

        {/* Execute Button */}
        <div className="mt-4">
          <Button
            onClick={handleExecute}
            disabled={executing}
            className="px-6 bg-green-600 text-white"
          >
            {executing ? 'Executing...' : 'Run Code'}
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}
      </Card>

      {/* Results Section */}
      {result && (
        <Card>
          <h2 className="text-2xl font-bold mb-4">📊 Results</h2>

          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="p-3 bg-gray-50 rounded-lg text-center">
              <p className="text-sm text-gray-600">Status</p>
              <p className={`font-bold text-lg ${getStatusColor(result.status)}`}>
                {result.status.toUpperCase().replace('_', ' ')}
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg text-center">
              <p className="text-sm text-gray-600">Passed</p>
              <p className="font-bold text-lg text-green-600">
                {result.test_cases_passed}/{result.test_cases_total}
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg text-center">
              <p className="text-sm text-gray-600">Time</p>
              <p className="font-bold text-lg">
                {result.execution_time_ms ? `${result.execution_time_ms}ms` : 'N/A'}
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg text-center">
              <p className="text-sm text-gray-600">Points</p>
              <p className="font-bold text-lg text-blue-600">{result.points_earned}</p>
            </div>
          </div>

          {/* Compilation Log */}
          {result.compilation_log && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="font-bold text-red-800 mb-2">Compilation Error</p>
              <pre className="text-sm text-red-700 overflow-auto max-h-40">
                {result.compilation_log}
              </pre>
            </div>
          )}

          {/* Error Message */}
          {result.error_message && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="font-bold text-red-800 mb-2">Error</p>
              <p className="text-sm text-red-700">{result.error_message}</p>
            </div>
          )}

          {/* Test Cases */}
          <div className="space-y-3">
            <h3 className="font-bold">Test Cases</h3>
            {result.test_results.map((testResult) => (
              <div
                key={testResult.test_case_number}
                className={`p-4 border rounded-lg ${
                  testResult.passed ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="font-bold">Test Case #{testResult.test_case_number}</span>
                    <span
                      className={`ml-3 px-2 py-1 rounded text-xs font-semibold ${getTestCaseStatusColor(testResult.passed)}`}
                    >
                      {testResult.passed ? '✓ PASSED' : '✗ FAILED'}
                    </span>
                  </div>
                </div>

                {/* Input/Output */}
                <div className="space-y-2 text-sm font-mono">
                  <div>
                    <p className="text-gray-600">Input:</p>
                    <p className="bg-white p-2 rounded border border-gray-200">
                      {testResult.input_data || '(empty)'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Expected:</p>
                    <p className="bg-white p-2 rounded border border-gray-200">
                      {testResult.expected_output}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Actual:</p>
                    <p
                      className={`p-2 rounded border ${
                        testResult.passed
                          ? 'bg-green-50 border-green-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      {testResult.actual_output || '(no output)'}
                    </p>
                  </div>

                  {testResult.error_message && (
                    <div>
                      <p className="text-red-600">Error:</p>
                      <p className="bg-red-50 p-2 rounded border border-red-200 text-red-700">
                        {testResult.error_message}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default CodeExecutor;
