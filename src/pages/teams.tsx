import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { API_BASE } from '@/lib/api';

interface Team {
  id: number;
  name: string;
  slug: string;
  description: string;
  owner_id: number;
  visibility: string;
  icon_emoji?: string;
  banner_url?: string;
  member_count: number;
  total_points: number;
  average_rating: number;
  has_contests: boolean;
  has_analytics: boolean;
  created_at: string;
}

interface UserTeamStats {
  total_teams: number;
  teams_owned: number;
  teams_member: number;
  active_teams: number;
  total_team_points: number;
}

export default function TeamsPage() {
  const router = useRouter();
  const [teams, setTeams] = useState<Team[]>([]);
  const [stats, setStats] = useState<UserTeamStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [tab, setTab] = useState<'my-teams' | 'discover'>('my-teams');
  
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    visibility: 'private',
    icon_emoji: '👥',
    max_members: 50,
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchUserStats();
    fetchMyTeams();
  }, []);

  const fetchUserStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/teams/user/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchMyTeams = async () => {
    try {
      setLoading(true);
      // For now, show teams via discovery since we don't have a dedicated my-teams endpoint
      // In production, create a specific /my-teams endpoint
      const response = await fetch(`${API_BASE}/api/v1x/teams/discover?page=1&page_size=20`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTeams(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/api/v1x/teams/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Failed to create team');
      
      const newTeam = await response.json();
      setTeams([newTeam, ...teams]);
      setShowCreateForm(false);
      setFormData({
        name: '',
        slug: '',
        description: '',
        visibility: 'private',
        icon_emoji: '👥',
        max_members: 50,
      });
      fetchUserStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const visitTeam = (slug: string) => {
    router.push(`/teams/${slug}`);
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {/* Header */}
        <div className="bg-white border-b border-slate-200">
          <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-slate-900">👥 Teams & Groups</h1>
                <p className="text-slate-600 mt-2">Collaborate with others and learn together</p>
              </div>
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                ✨ Create Team
              </Button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
              <Card className="bg-white p-6">
                <div className="text-slate-600 text-sm font-semibold">Total Teams</div>
                <div className="text-3xl font-bold text-slate-900">{stats.total_teams}</div>
              </Card>
              <Card className="bg-white p-6">
                <div className="text-slate-600 text-sm font-semibold">Teams Owned</div>
                <div className="text-3xl font-bold text-blue-600">{stats.teams_owned}</div>
              </Card>
              <Card className="bg-white p-6">
                <div className="text-slate-600 text-sm font-semibold">Teams Joined</div>
                <div className="text-3xl font-bold text-green-600">{stats.teams_member}</div>
              </Card>
              <Card className="bg-white p-6">
                <div className="text-slate-600 text-sm font-semibold">Active Teams</div>
                <div className="text-3xl font-bold text-purple-600">{stats.active_teams}</div>
              </Card>
              <Card className="bg-white p-6">
                <div className="text-slate-600 text-sm font-semibold">Total Points</div>
                <div className="text-3xl font-bold text-yellow-600">{stats.total_team_points}</div>
              </Card>
            </div>
          )}

          {/* Create Team Form */}
          {showCreateForm && (
            <Card className="bg-white p-8 mb-8 border border-blue-200">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Create New Team</h2>
              <form onSubmit={handleCreateTeam} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Team Name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="e.g., JavaScript Masters"
                    required
                  />
                  <Input
                    label="Team Slug"
                    value={formData.slug}
                    onChange={(e) => handleInputChange('slug', e.target.value.toLowerCase().replace(/\s+/g, '-'))}
                    placeholder="e.g., javascript-masters"
                    pattern="^[a-z0-9-]+$"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Team Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Describe your team's goals and focus areas..."
                    rows={4}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Icon Emoji</label>
                    <Input
                      value={formData.icon_emoji}
                      onChange={(e) => handleInputChange('icon_emoji', e.target.value)}
                      placeholder="👥"
                      maxLength={1}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Visibility</label>
                    <select
                      value={formData.visibility}
                      onChange={(e) => handleInputChange('visibility', e.target.value)}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="private">🔒 Private</option>
                      <option value="public">🌐 Public</option>
                      <option value="restricted">🔗 Restricted</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Max Members</label>
                    <Input
                      type="number"
                      value={formData.max_members}
                      onChange={(e) => handleInputChange('max_members', parseInt(e.target.value))}
                      min="5"
                      max="500"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    ✓ Create Team
                  </Button>
                  <Button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
              {error}
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-slate-200">
            <button
              onClick={() => {
                setTab('my-teams');
                fetchMyTeams();
              }}
              className={`px-4 py-3 font-semibold border-b-2 transition ${
                tab === 'my-teams'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              👤 My Teams ({stats?.total_teams || 0})
            </button>
            <button
              onClick={() => {
                setTab('discover');
                fetchMyTeams();
              }}
              className={`px-4 py-3 font-semibold border-b-2 transition ${
                tab === 'discover'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              🌐 Discover Teams
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin">⏳</div>
              <p className="text-slate-600 mt-2">Loading teams...</p>
            </div>
          ) : (
            <>
              {teams.length === 0 ? (
                <Card className="bg-white p-8 text-center">
                  <div className="text-4xl mb-4">👥</div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">
                    {tab === 'my-teams' ? 'No Teams Yet' : 'No Teams Found'}
                  </h3>
                  <p className="text-slate-600 mb-4">
                    {tab === 'my-teams'
                      ? 'Create a team to get started or join existing teams'
                      : 'Check back later for public teams'}
                  </p>
                  {tab === 'my-teams' && (
                    <Button onClick={() => setShowCreateForm(true)}>Create Your First Team</Button>
                  )}
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {teams.map((team) => (
                    <Card
                      key={team.id}
                      className="bg-white overflow-hidden hover:shadow-lg transition cursor-pointer group"
                      onClick={() => visitTeam(team.slug)}
                    >
                      {/* Banner */}
                      {team.banner_url ? (
                        <div
                          className="h-32 bg-cover bg-center"
                          style={{ backgroundImage: `url(${team.banner_url})` }}
                        />
                      ) : (
                        <div className="h-32 bg-gradient-to-br from-blue-400 to-blue-600" />
                      )}

                      {/* Content */}
                      <div className="p-6">
                        <div className="flex items-center gap-3 mb-3">
                          <span className="text-3xl">{team.icon_emoji || '👥'}</span>
                          <div>
                            <h3 className="font-bold text-slate-900 text-lg group-hover:text-blue-600 transition">
                              {team.name}
                            </h3>
                            <p className="text-xs text-slate-500">{team.visibility}</p>
                          </div>
                        </div>

                        <p className="text-sm text-slate-600 mb-4 line-clamp-2">{team.description}</p>

                        <div className="flex gap-2 mb-4 flex-wrap">
                          {team.has_contests && (
                            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">🏆 Contests</span>
                          )}
                          {team.has_analytics && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">📊 Analytics</span>
                          )}
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-center py-3 border-y border-slate-200">
                          <div>
                            <div className="text-sm font-bold text-slate-900">{team.member_count}</div>
                            <div className="text-xs text-slate-600">Members</div>
                          </div>
                          <div>
                            <div className="text-sm font-bold text-slate-900">{team.total_points}</div>
                            <div className="text-xs text-slate-600">Points</div>
                          </div>
                          <div>
                            <div className="text-sm font-bold text-slate-900">{team.average_rating.toFixed(1)}</div>
                            <div className="text-xs text-slate-600">Rating</div>
                          </div>
                        </div>

                        <Button
                          onClick={(e) => {
                            e.stopPropagation();
                            visitTeam(team.slug);
                          }}
                          className="w-full mt-4 bg-blue-600 hover:bg-blue-700"
                        >
                          View Team →
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
