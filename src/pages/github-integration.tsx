import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";
import { Github, ExternalLink, Code2, GitBranch } from "lucide-react";

interface GitHubAccount {
  github_username: string;
  github_name: string;
  github_bio: string;
  github_avatar_url: string;
  github_profile_url: string;
  public_repos_count: number;
  followers_count: number;
  following_count: number;
  connected_at: string;
  last_synced_at: string;
}

interface Repository {
  id: number;
  repo_name: string;
  repo_full_name: string;
  repo_description: string;
  repo_url: string;
  stars_count: number;
  forks_count: number;
  primary_language: string;
  total_commits: number;
  user_commits: number;
}

export default function GitHubIntegrationPage() {
  const router = useRouter();
  const [account, setAccount] = useState<GitHubAccount | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchGitHubAccount();
  }, []);

  const fetchGitHubAccount = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/github/account`,
        { credentials: "include" }
      );
      const data = await response.json();
      
      if (data.connected) {
        setAccount(data.account);
        setConnected(true);
        fetchRepositories();
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch GitHub account:", error);
      setLoading(false);
    }
  };

  const fetchRepositories = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/github/repositories`,
        { credentials: "include" }
      );
      const data = await response.json();
      setRepositories(data.repositories || []);
    } catch (error) {
      console.error("Failed to fetch repositories:", error);
    }
  };

  const handleConnect = () => {
    // Redirect to GitHub OAuth
    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || "YOUR_CLIENT_ID";
    const redirectUri = `${window.location.origin}/github-callback`;
    const scope = "user:email,public_repo,repo,read:user";
    
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
    window.location.href = authUrl;
  };

  const handleDisconnect = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/github/disconnect`,
        { method: "POST", credentials: "include" }
      );
      if (response.ok) {
        setConnected(false);
        setAccount(null);
        setRepositories([]);
      }
    } catch (error) {
      console.error("Failed to disconnect:", error);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/github/sync-repositories`,
        { method: "POST", credentials: "include" }
      );
      if (response.ok) {
        setTimeout(() => {
          fetchRepositories();
          setSyncing(false);
        }, 2000);
      }
    } catch (error) {
      console.error("Failed to sync:", error);
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading GitHub integration...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <Github className="w-10 h-10 text-slate-300" />
              <SectionHeading className="text-white mb-0">GitHub Integration</SectionHeading>
            </div>
            <p className="text-slate-300 text-lg">
              Connect your GitHub account to showcase your repositories and contributions on your SkillForge profile.
            </p>
          </div>

          {!connected ? (
            // Not Connected State
            <Card className="bg-slate-800 border-slate-700 mb-12">
              <div className="text-center py-12">
                <Github className="w-16 h-16 text-slate-400 mx-auto mb-6" />
                <h2 className="text-2xl font-bold text-white mb-4">Connect Your GitHub Account</h2>
                <p className="text-slate-300 mb-8 max-w-md mx-auto">
                  Link your GitHub profile to automatically sync your repositories and contributions.
                </p>
                <Button className="px-8 py-3" onClick={handleConnect}>
                  <Github className="w-5 h-5 inline-block mr-2" />
                  Connect with GitHub
                </Button>
              </div>
            </Card>
          ) : account ? (
            // Connected State
            <>
              {/* Profile Card */}
              <Card className="bg-gradient-to-r from-slate-800 to-slate-700 border-slate-600 mb-8">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-6">
                    <img
                      src={account.github_avatar_url}
                      alt={account.github_username}
                      className="w-20 h-20 rounded-full"
                    />
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">
                        {account.github_name || account.github_username}
                      </h2>
                      <p className="text-slate-400 mb-4">@{account.github_username}</p>
                      {account.github_bio && (
                        <p className="text-slate-300 mb-4">{account.github_bio}</p>
                      )}
                      <div className="flex gap-6 text-sm text-slate-300">
                        <span>📦 {account.public_repos_count} repositories</span>
                        <span>👥 {account.followers_count} followers</span>
                        <span>⭐ Following {account.following_count}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <a
                      href={account.github_profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition"
                    >
                      View Profile
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    <button
                      onClick={handleDisconnect}
                      className="px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition font-medium text-sm"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
              </Card>

              {/* Sync Section */}
              <div className="mb-8 flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Repositories</h3>
                  <p className="text-slate-400">
                    Last synced: {account.last_synced_at ? new Date(account.last_synced_at).toLocaleDateString() : "Never"}
                  </p>
                </div>
                <Button
                  onClick={handleSync}
                  disabled={syncing}
                  variant="secondary"
                >
                  {syncing ? "Syncing..." : "Sync Now"}
                </Button>
              </div>

              {/* Repositories List */}
              {repositories.length > 0 ? (
                <div className="grid gap-4">
                  {repositories.map(repo => (
                    <Card key={repo.id} className="bg-slate-800 border-slate-700 hover:border-blue-500/50 transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <a
                            href={repo.repo_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lg font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-2 mb-2"
                          >
                            <Code2 className="w-5 h-5" />
                            {repo.repo_full_name}
                          </a>
                          
                          {repo.repo_description && (
                            <p className="text-slate-400 text-sm mb-3 line-clamp-2">
                              {repo.repo_description}
                            </p>
                          )}
                          
                          <div className="flex flex-wrap gap-4 text-xs text-slate-400">
                            {repo.primary_language && (
                              <span className="flex items-center gap-1">
                                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                                {repo.primary_language}
                              </span>
                            )}
                            <span>⭐ {repo.stars_count} stars</span>
                            <span>🔀 {repo.forks_count} forks</span>
                            <span>
                              <GitBranch className="w-3 h-3 inline-block mr-1" />
                              {repo.total_commits} commits
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-400 mb-1">
                            {repo.user_commits}
                          </div>
                          <div className="text-xs text-slate-400">your commits</div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="bg-slate-800 border-slate-700 text-center py-12">
                  <p className="text-slate-400">No repositories found. Try syncing your account.</p>
                </Card>
              )}
            </>
          ) : null}
        </div>
      </div>
    </Layout>
  );
}
