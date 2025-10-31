import { useEffect, useState } from 'react';
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

  useEffect(() => {
    if (!userLoading && !user) {
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
      } else if (response.status === 401) {
        // Not authenticated: send to login with redirect
        router.push('/login?redirect=/resumes/new');
        return;
      } else {
        console.error('Failed to create resume');
        alert('Failed to create resume. Please try again.');
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
