'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Layout from '@/components/Layout';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { Star } from 'lucide-react';

interface Mentor {
  id: number;
  user_id: number;
  name: string;
  bio: string;
  expertise: string;
  hourly_rate: number;
  status: string;
  average_rating: number;
  total_sessions?: number;
}

export default function BookSession() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('user');
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMentors();
  }, []);

  const loadMentors = async () => {
    try {
      setLoading(true);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const response = await fetch(`${apiBase}/api/v1x/mentors?limit=100`);
      
      if (!response.ok) {
        throw new Error(`Failed to load mentors: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      // Response is a list directly, not wrapped in 'data' field
      const mentorsList = Array.isArray(data) ? data : (data.data || data.mentors || []);
      const approvedMentors = mentorsList.filter(
        (m: any) => m && (m.status === 'APPROVED' || m.status === 'approved')
      );
      
      setMentors(approvedMentors);
      setError(null);
    } catch (err) {
      console.error('Error loading mentors:', err);
      setError(err instanceof Error ? err.message : 'Failed to load mentors');
      setMentors([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout maxWidth="2xl">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout maxWidth="2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Book a Mentor Session</h1>
        <p className="text-gray-600">Select a mentor to view their available time slots</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}

      {mentors.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No mentors available at this time</p>
            <Link href="/mentors">
              <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Explore All Mentors
              </button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {mentors.map((mentor) => (
            <Card key={mentor.id} className="hover:shadow-lg transition-shadow">
              <div className="flex flex-col h-full">
                {/* Header with name and rating */}
                <div className="mb-4">
                  <h2 className="text-xl font-bold text-gray-900 mb-1">
                    {mentor.name}
                  </h2>
                  <div className="flex items-center gap-1 mb-2">
                    <div className="flex text-yellow-400">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          size={16}
                          fill={i < Math.round(mentor.average_rating || 0) ? 'currentColor' : 'none'}
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">
                      {mentor.average_rating || 0} rating
                    </span>
                  </div>
                </div>

                {/* Bio */}
                <p className="text-gray-600 text-sm mb-4 flex-grow">
                  {mentor.bio}
                </p>

                {/* Expertise */}
                <div className="mb-4">
                  <p className="text-sm font-semibold text-gray-700 mb-1">Expertise:</p>
                  <div className="flex flex-wrap gap-2">
                    {mentor.expertise
                      ?.split(',')
                      .map((skill, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium"
                        >
                          {skill.trim()}
                        </span>
                      ))}
                  </div>
                </div>

                {/* Rate and Button */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-baseline gap-1">
                    <span className="text-2xl font-bold text-gray-900">
                      ${mentor.hourly_rate}
                    </span>
                    <span className="text-gray-600 text-sm">/hour</span>
                  </div>
                  <Link href={`/student/book-session/${mentor.id}`}>
                    <button className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
                      Book Session
                    </button>
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </Layout>
  );
}
