import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface UserProfile {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  bio: string;
  role: string;
  skills: string[];
  followers: number;
  following: number;
  postsCount: number;
  courses: Array<{ id: number; title: string; progress: number }>;
  achievements: Array<{ id: number; name: string; icon: string }>;
  isFollowing: boolean;
}

export default function UserProfilePage() {
  const router = useRouter();
  const { userId } = router.query;
  const { user: currentUser, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('about');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (userId) {
      fetchProfile();
    }
  }, [isAuthenticated, userId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/profiles/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch profile');
      const data = await response.json();
      setProfile(data.profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading profile');
      console.error('Profile fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowClick = async () => {
    if (!profile) return;

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      await fetch(`${apiBase}/api/v1x/profiles/${profile.id}/follow`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      fetchProfile();
    } catch (err) {
      console.error('Follow error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{profile?.name} - SkillForge</title>
        <meta name="description" content={profile?.bio} />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {error && (
          <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg m-4">
            {error}
          </div>
        )}

        {profile && (
          <>
            {/* Profile Header */}
            <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
              <div className="max-w-4xl mx-auto px-4 py-12">
                <div className="flex flex-col md:flex-row items-start gap-8">
                  {/* Avatar */}
                  <img
                    src={profile.avatar || `https://ui-avatars.com/api/?name=${profile.name}&size=200&background=random`}
                    alt={profile.name}
                    className="w-32 h-32 rounded-full border-4 border-gray-300 dark:border-gray-600"
                  />

                  {/* Info */}
                  <div className="flex-1">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                      {profile.name}
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {profile.role}
                    </p>
                    <p className="text-gray-700 dark:text-gray-300 max-w-lg mb-6">
                      {profile.bio}
                    </p>

                    {/* Stats */}
                    <div className="flex gap-8 mb-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {profile.followers}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Followers
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {profile.following}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Following
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {profile.postsCount}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Posts
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    {currentUser?.id !== profile.id ? (
                      <div className="flex gap-3">
                        <button
                          onClick={handleFollowClick}
                          className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                            profile.isFollowing
                              ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                              : 'bg-blue-600 hover:bg-blue-700 text-white'
                          }`}
                        >
                          {profile.isFollowing ? '✓ Following' : '+ Follow'}
                        </button>
                        <Link href={`/messages?user=${profile.id}`}>
                          <button className="px-6 py-2 rounded-lg font-semibold bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
                            💌 Message
                          </button>
                        </Link>
                      </div>
                    ) : (
                      <Link href="/settings/profile">
                        <button className="px-6 py-2 rounded-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-colors">
                          ✏️ Edit Profile
                        </button>
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="max-w-4xl mx-auto px-4">
              <div className="flex gap-6 border-b border-gray-200 dark:border-gray-700 my-8">
                {[
                  { id: 'about', label: 'About' },
                  { id: 'skills', label: 'Skills' },
                  { id: 'courses', label: 'Courses' },
                  { id: 'achievements', label: 'Achievements' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`pb-4 font-semibold transition-colors ${
                      activeTab === tab.id
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Content */}
              <div className="pb-12">
                {activeTab === 'about' && (
                  <div className="space-y-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {profile.bio}
                    </p>
                  </div>
                )}

                {activeTab === 'skills' && (
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.length === 0 ? (
                      <p className="text-gray-600 dark:text-gray-400">No skills added yet</p>
                    ) : (
                      profile.skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 text-sm font-semibold"
                        >
                          {skill}
                        </span>
                      ))
                    )}
                  </div>
                )}

                {activeTab === 'courses' && (
                  <div className="space-y-4">
                    {profile.courses.length === 0 ? (
                      <p className="text-gray-600 dark:text-gray-400">No courses started yet</p>
                    ) : (
                      profile.courses.map((course) => (
                        <div
                          key={course.id}
                          className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
                        >
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                            {course.title}
                          </h3>
                          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-600"
                              style={{ width: `${course.progress}%` }}
                            />
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                            {course.progress}% complete
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {activeTab === 'achievements' && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {profile.achievements.length === 0 ? (
                      <p className="col-span-full text-gray-600 dark:text-gray-400">
                        No achievements unlocked yet
                      </p>
                    ) : (
                      profile.achievements.map((achievement) => (
                        <div
                          key={achievement.id}
                          className="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-center"
                        >
                          <div className="text-4xl mb-2">{achievement.icon}</div>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">
                            {achievement.name}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
