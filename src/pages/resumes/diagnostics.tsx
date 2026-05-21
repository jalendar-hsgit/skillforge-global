/**
 * Resume API Diagnostics Page
 * Tests if the resume endpoints are working correctly
 */
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { useMe } from '@/hooks/useMe';

export default function ResumeDiagnosticsPage() {
  const router = useRouter();
  const { me: user, loading: userLoading } = useMe();
  const [results, setResults] = useState<any>({});
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/login?redirect=/resumes/diagnostics');
    }
  }, [user, userLoading, router]);

  const testEndpoints = async () => {
    setTesting(true);
    const testResults: any = {};

    // Test 1: List resumes
    try {
      const res = await fetch('/api/session/resumes', {
        method: 'GET',
        credentials: 'include',
      });
      testResults.listResumes = {
        status: res.status,
        ok: res.ok,
        data: res.ok ? await res.json() : await res.text(),
      };
    } catch (e: any) {
      testResults.listResumes = { error: e.message };
    }

    // Test 2: Get resume by ID (if any exist)
    if (testResults.listResumes.ok && testResults.listResumes.data?.length > 0) {
      const resumeId = testResults.listResumes.data[0].id;
      try {
        const res = await fetch(`/api/session/resumes?id=${resumeId}`, {
          method: 'GET',
          credentials: 'include',
        });
        testResults.getResume = {
          status: res.status,
          ok: res.ok,
          data: res.ok ? await res.json() : await res.text(),
        };
      } catch (e: any) {
        testResults.getResume = { error: e.message };
      }
    }

    // Test 3: Backend health
    try {
      const res = await fetch('/api/session/v1x/healthz');
      testResults.backendHealth = {
        status: res.status,
        ok: res.ok,
        data: res.ok ? await res.json() : await res.text(),
      };
    } catch (e: any) {
      testResults.backendHealth = { error: e.message };
    }

    setResults(testResults);
    setTesting(false);
  };

  if (userLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-6">Resume API Diagnostics</h1>
        
        <div className="mb-6">
          <button
            onClick={testEndpoints}
            disabled={testing}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {testing ? 'Testing...' : 'Run Tests'}
          </button>
        </div>

        {Object.keys(results).length > 0 && (
          <div className="space-y-6">
            {Object.entries(results).map(([key, value]: [string, any]) => (
              <div key={key} className="border rounded-lg p-4 bg-white shadow">
                <h3 className="font-bold text-lg mb-2 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </h3>
                <div className="space-y-2">
                  {value.status && (
                    <p>
                      <span className="font-semibold">Status:</span>{' '}
                      <span className={value.ok ? 'text-green-600' : 'text-red-600'}>
                        {value.status} {value.ok ? '✓' : '✗'}
                      </span>
                    </p>
                  )}
                  {value.error && (
                    <p className="text-red-600">
                      <span className="font-semibold">Error:</span> {value.error}
                    </p>
                  )}
                  {value.data && (
                    <div>
                      <p className="font-semibold mb-1">Data:</p>
                      <pre className="bg-gray-100 p-3 rounded text-xs overflow-auto max-h-64">
                        {JSON.stringify(value.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-bold mb-2">Expected Routes:</h3>
          <ul className="space-y-1 text-sm">
            <li>• GET /api/session/resumes - List all resumes</li>
            <li>• GET /api/session/resumes?id=123 - Get resume by ID</li>
            <li>• POST /api/session/resumes - Create resume</li>
            <li>• PATCH /api/session/resumes?id=123 - Update resume</li>
            <li>• DELETE /api/session/resumes?id=123 - Delete resume</li>
          </ul>
        </div>

        <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
          <h3 className="font-bold mb-2">Current User:</h3>
          <pre className="text-xs overflow-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>
      </div>
    </Layout>
  );
}
