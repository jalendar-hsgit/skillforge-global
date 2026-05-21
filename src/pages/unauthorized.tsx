import Layout from '@/components/Layout';
import Link from 'next/link';
import { AlertTriangle, Home, Mail } from 'lucide-react';

export default function UnauthorizedPage() {
  return (
    <Layout>
      <div className="flex items-center justify-center min-h-screen bg-white dark:bg-gray-900 px-4">
        <div className="text-center max-w-md">
          <div className="mb-6">
            <AlertTriangle 
              size={64} 
              className="mx-auto text-yellow-500 dark:text-yellow-400"
            />
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Access Denied
          </h1>
          
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
            You don't have permission to access this page.
          </p>

          <p className="text-sm text-gray-500 dark:text-gray-500 mb-8">
            This page requires special access or permissions. If you believe you should have access, 
            please contact support.
          </p>

          <div className="space-y-3">
            <Link
              href="/"
              className="inline-flex items-center justify-center gap-2 w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              <Home size={20} />
              Back to Home
            </Link>

            <a
              href="mailto:support@skillforge.com"
              className="inline-flex items-center justify-center gap-2 w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              <Mail size={20} />
              Contact Support
            </a>
          </div>

          <p className="mt-8 text-xs text-gray-400 dark:text-gray-600">
            Error: 403 Forbidden
          </p>
        </div>
      </div>
    </Layout>
  );
}
