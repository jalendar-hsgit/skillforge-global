import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { useMe } from '@/hooks/useMe';
import ResumeEditor from '@/components/resume/ResumeEditor';

/**
 * Resume view/edit page at /resumes/[id]
 * This serves as both the view and edit interface for a resume
 */
export default function ResumePage() {
  const router = useRouter();
  const { id } = router.query;
  const { me: user, loading: userLoading } = useMe();

  useEffect(() => {
    if (!userLoading && !user) {
      router.push(`/login?redirect=/resumes/${id}`);
    }
  }, [user, userLoading, router, id]);

  if (userLoading || !id) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading resume...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>Resume Editor - SkillForge Global</title>
      </Head>
      <ResumeEditor resumeId={parseInt(id as string)} />
    </>
  );
}
