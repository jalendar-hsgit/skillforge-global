import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";

interface Challenge {
  id: number;
  challenge_id: number;
  order: number;
  points_value: number;
  estimated_minutes: number;
}

interface PathProgress {
  id: number;
  completed_challenges: number;
  total_challenges: number;
  completion_percentage: number;
  is_completed: boolean;
  total_points_earned: number;
  current_challenge_id: number;
}

interface PathDetail {
  path: {
    id: number;
    title: string;
    description: string;
    icon: string;
    difficulty: string;
    estimated_hours: number;
    total_challenges: number;
  };
  challenges: Challenge[];
  user_progress: PathProgress | null;
}

export default function LearningPathDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [pathDetail, setPathDetail] = useState<PathDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchPathDetail();
  }, [id]);

  const fetchPathDetail = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/paths/${id}`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setPathDetail(data);
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch path detail:", error);
      setLoading(false);
    }
  };

  const completeChallenge = async (challengeId: number) => {
    if (!id || !pathDetail) return;
    
    setCompleting(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/paths/${id}/challenges/${challengeId}/complete`,
        {
          method: "POST",
          credentials: "include"
        }
      );
      if (response.ok) {
        const data = await response.json();
        setPathDetail(prev => prev ? {
          ...prev,
          user_progress: data.progress
        } : null);
      }
    } catch (error) {
      console.error("Failed to complete challenge:", error);
    }
    setCompleting(false);
  };

  if (loading || !pathDetail) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading path...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const { path, challenges, user_progress } = pathDetail;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Path Header */}
          <div className="mb-12">
            <div className="flex items-start gap-6 mb-6">
              <div className="text-6xl">{path.icon || "📚"}</div>
              <div className="flex-1">
                <SectionHeading className="text-white mb-2">{path.title}</SectionHeading>
                <p className="text-slate-300 text-lg mb-4">{path.description}</p>
                <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                  <span>📊 Difficulty: {path.difficulty}</span>
                  <span>⏱️ {path.estimated_hours} hours</span>
                  <span>🎯 {path.total_challenges} challenges</span>
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            {user_progress && (
              <Card className="bg-slate-800 border-slate-700">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-white font-semibold">Your Progress</span>
                    <span className="text-2xl font-bold text-blue-400">
                      {user_progress.completion_percentage.toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all"
                      style={{ width: `${user_progress.completion_percentage}%` }}
                    />
                  </div>
                  <div className="text-sm text-slate-400">
                    {user_progress.completed_challenges} of {user_progress.total_challenges} challenges completed
                  </div>
                  <div className="text-sm text-yellow-400">
                    💰 {user_progress.total_points_earned} points earned
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Challenges List */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white mb-6">Challenges</h2>
            
            {challenges.map((challenge, index) => {
              const isCompleted = user_progress && challenge.order < user_progress.completed_challenges;
              const isCurrentChallenge = user_progress && challenge.id === user_progress.current_challenge_id;

              return (
                <Card
                  key={challenge.id}
                  className={`border-2 transition ${
                    isCurrentChallenge
                      ? "bg-slate-700 border-blue-500 shadow-lg shadow-blue-500/20"
                      : isCompleted
                      ? "bg-slate-800 border-green-500/30"
                      : "bg-slate-800 border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                        isCompleted
                          ? "bg-green-600 text-white"
                          : isCurrentChallenge
                          ? "bg-blue-600 text-white"
                          : "bg-slate-700 text-slate-300"
                      }`}>
                        {isCompleted ? "✓" : index + 1}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white">
                          Challenge {index + 1}
                        </h3>
                        <div className="flex gap-4 mt-2 text-sm text-slate-400">
                          <span>ID: {challenge.challenge_id}</span>
                          <span>⏱️ {challenge.estimated_minutes} min</span>
                          <span>💰 {challenge.points_value} points</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      {isCompleted ? (
                        <button className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium cursor-default">
                          ✓ Completed
                        </button>
                      ) : isCurrentChallenge ? (
                        <Button
                          onClick={() => completeChallenge(challenge.id)}
                          disabled={completing}
                        >
                          {completing ? "Completing..." : "Complete Challenge"}
                        </Button>
                      ) : (
                        <button
                          className="px-6 py-2 bg-slate-700 text-slate-300 rounded-lg font-medium cursor-not-allowed"
                          disabled
                        >
                          Locked
                        </button>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Completion Status */}
          {user_progress?.is_completed && (
            <Card className="mt-12 bg-gradient-to-r from-green-900/50 to-emerald-900/50 border-green-500/30">
              <div className="text-center py-8">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-3xl font-bold text-green-400 mb-2">Path Completed!</h2>
                <p className="text-slate-300">
                  Congratulations! You've completed all challenges in this path.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}
