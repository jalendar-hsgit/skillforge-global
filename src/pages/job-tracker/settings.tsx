'use client';

import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import JobNotifications from '@/components/job-tracker/JobNotifications';
import { DownloadAllInterviews } from '@/components/job-tracker/CalendarExport';
import { ArrowLeft, Settings as SettingsIcon, Bell, Calendar, Download, Mail } from 'lucide-react';

export default function JobTrackerSettings() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Job Tracker Settings | SkillForge Global</title>
      </Head>

      <Layout>
        <div className="max-w-5xl mx-auto px-4 py-8">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Job Tracker
          </button>

          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3 mb-8">
            <SettingsIcon className="w-10 h-10 text-blue-600" />
            Job Tracker Settings
          </h1>

          {/* Email Notifications */}
          <div className="mb-8">
            <JobNotifications />
          </div>

          {/* Calendar Export */}
          <div className="mb-8">
            <DownloadAllInterviews />
          </div>

          {/* Email Templates */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Mail className="w-6 h-6 text-green-600" />
              Follow-up Email Templates
            </h3>

            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-2">1 Week Follow-up</h4>
                <p className="text-sm text-gray-700 mb-2">Use this template 1 week after applying:</p>
                <div className="bg-white p-3 rounded border border-gray-300 text-sm font-mono">
                  <p className="text-gray-800">
                    Subject: Following up on [Position] Application
                    <br /><br />
                    Dear Hiring Manager,
                    <br /><br />
                    I hope this email finds you well. I recently applied for the [Position] role at [Company] and wanted to follow up on my application.
                    <br /><br />
                    I'm very excited about the opportunity to contribute to [Company] and would love to discuss how my skills in [Key Skills] align with your needs.
                    <br /><br />
                    Please let me know if you need any additional information from me.
                    <br /><br />
                    Thank you for your time and consideration.
                    <br /><br />
                    Best regards,
                    <br />
                    [Your Name]
                  </p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-2">Post-Interview Thank You</h4>
                <p className="text-sm text-gray-700 mb-2">Send within 24 hours after interview:</p>
                <div className="bg-white p-3 rounded border border-gray-300 text-sm font-mono">
                  <p className="text-gray-800">
                    Subject: Thank you for the [Position] interview
                    <br /><br />
                    Dear [Interviewer Name],
                    <br /><br />
                    Thank you for taking the time to speak with me today about the [Position] role at [Company]. I enjoyed learning more about the team and the exciting projects you're working on.
                    <br /><br />
                    Our conversation reinforced my enthusiasm for this opportunity, particularly [specific topic discussed].
                    <br /><br />
                    Please feel free to reach out if you need any additional information. I look forward to hearing from you about the next steps.
                    <br /><br />
                    Best regards,
                    <br />
                    [Your Name]
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Tips & Best Practices */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-xl font-bold text-blue-900 mb-4">💡 Best Practices</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-blue-800 text-sm">
              <div>
                <h4 className="font-semibold mb-2">Email Notifications:</h4>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Check notifications daily</li>
                  <li>Send follow-ups on weekday mornings</li>
                  <li>Keep emails brief and professional</li>
                  <li>Always personalize the content</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Calendar Management:</h4>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Export interviews to your main calendar</li>
                  <li>Set reminders 1 day and 1 hour before</li>
                  <li>Block 15 mins prep time before interviews</li>
                  <li>Add travel/tech setup time</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
