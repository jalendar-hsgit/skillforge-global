import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { useMe } from '@/hooks/useMe';
import ResumeEditor from '@/components/resume/ResumeEditor';

export default function NewResumePage() {
  const router = useRouter();
  const { me: user, loading: userLoading } = useMe();
  const [creatingResume, setCreatingResume] = useState(false);
  const [resumeId, setResumeId] = useState<number | null>(null);
  const hasRedirected = useRef(false);

  useEffect(() => {
    if (!userLoading && !user && !hasRedirected.current) {
      hasRedirected.current = true;
      router.push('/login?redirect=/resumes/new');
    }
  }, [user, userLoading, router]);

  useEffect(() => {
    if (user && !resumeId && !creatingResume) {
      createInitialResume();
    }
  }, [user, resumeId, creatingResume]);

  const createInitialResume = async () => {
    setCreatingResume(true);
    try {
      // Create via Next.js proxy so HttpOnly cookie is forwarded automatically
      const response = await fetch('/api/session/resumes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title: 'Untitled Resume',
          template: 'modern',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResumeId(data.id);
      } else if (response.status === 401 && !hasRedirected.current) {
        // Not authenticated: send to login with redirect
        hasRedirected.current = true;
        router.push('/login?redirect=/resumes/new');
        return;
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Failed to create resume:', response.status, errorData);
        alert(`Failed to create resume: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating resume:', error);
      alert('Failed to create resume. Please try again.');
    } finally {
      setCreatingResume(false);
    }
  };

  if (userLoading || creatingResume || !resumeId) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">
              {creatingResume ? 'Creating your resume...' : 'Loading...'}
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>New Resume - SkillForge Global</title>
      </Head>
      <ResumeEditor resumeId={resumeId} />
    </>
  );
}

// Server-side auth guard for reliable redirect
export async function getServerSideProps(context: any) {
  try {
    const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8001';
    const cookie = context.req?.headers?.cookie || '';
    const r = await fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { cookie },
    });
    if (r.status === 401) {
      return {
        redirect: {
          destination: `/login?redirect=/resumes/new`,
          permanent: false,
        },
      };
    }
  } catch (_) {
    // If backend not reachable, allow page to render and client-side will handle
  }
  return { props: {} };
}
