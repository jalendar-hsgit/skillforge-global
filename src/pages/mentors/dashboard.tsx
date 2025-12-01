import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';
import AvailabilityCalendar from '@/components/AvailabilityCalendar';
import { MentorProfile, SessionResponse, SessionListResponse } from '@/types/mentor';

// Using shared types from '@/types/mentor'

interface Availability {
  id: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export default function MentorDashboard() {
  const router = useRouter();
  
  const [mentorProfile, setMentorProfile] = useState<MentorProfile | null>(null);
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [availability, setAvailability] = useState<Availability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [activeTab, setActiveTab] = useState<'overview' | 'sessions' | 'availability'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch mentor profile
      const profileResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/me`,
        { credentials: 'include' }
      );

      if (profileResponse.status === 401) {
        router.push('/login?redirect=/mentors/dashboard');
        return;
      }

      if (profileResponse.status === 404) {
        // Not a mentor yet
        router.push('/mentors/become');
        return;
      }

      if (!profileResponse.ok) throw new Error('Failed to fetch profile');
      const profileData = await profileResponse.json();
      setMentorProfile(profileData);

      // Fetch sessions
      const sessionsResponse = await fetch(
        `${API_BASE}/api/v1x/mentors/sessions/my`,
        { credentials: 'include' }
      );
      if (sessionsResponse.ok) {
        const sessionsData: SessionListResponse | SessionResponse[] = await sessionsResponse.json();
        const list = Array.isArray(sessionsData) ? sessionsData : sessionsData.sessions;
        setSessions(Array.isArray(list) ? list : []);
      }

      // Fetch availability (if mentor is approved)
      if (profileData.status === 'approved') {
        const availabilityResponse = await fetch(
          `${API_BASE}/api/v1x/mentors/availability/${profileData.id}`,
          { credentials: 'include' }
        );
        if (availabilityResponse.ok) {
          const availabilityData = await availabilityResponse.json();
          setAvailability(availabilityData);
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      confirmed: 'bg-blue-100 text-blue-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };
  };
export { default } from './dashboard/index'
      </div>
    </Layout>
  );
}
