import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";

interface LearningPath {
  id: number;
  title: string;
  description: string;
  icon: string;
  difficulty: string;
  estimated_hours: number;
  total_challenges: number;
  is_featured: boolean;
}

interface PathProgress {
  id: number;
  path_id: number;
  completed_challenges: number;
  total_challenges: number;
  completion_percentage: number;
  is_completed: boolean;
}

export default function LearningPathsBrowser() {
  const router = useRouter();
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [userProgress, setUserProgress] = useState<Record<number, PathProgress>>({});
  const [loading, setLoading] = useState(true);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("");
  const [filteredPaths, setFilteredPaths] = useState<LearningPath[]>([]);

  useEffect(() => {
    fetchPaths();
    fetchUserProgress();
  }, []);

  useEffect(() => {
    if (selectedDifficulty) {
      setFilteredPaths(paths.filter(p => p.difficulty === selectedDifficulty));
    } else {
      setFilteredPaths(paths);
    }
  }, [selectedDifficulty, paths]);

  const fetchPaths = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/paths`);
      const data = await response.json();
      setPaths(data.paths || []);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch paths:", error);
      setLoading(false);
    }
  };

  const fetchUserProgress = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/paths/user/progress`, {
        credentials: "include"
      });
      if (response.ok) {
        const data = await response.json();
        const progressMap: Record<number, PathProgress> = {};
        data.progress.forEach((p: PathProgress) => {
          progressMap[p.path_id] = p;
        });
        setUserProgress(progressMap);
      }
    } catch (error) {
      console.error("Failed to fetch user progress:", error);
    }
  };

  const startPath = async (pathId: number) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/paths/${pathId}/start`, {
        method: "POST",
        credentials: "include"
      });
      if (response.ok) {
        const progress = await response.json();
        setUserProgress(prev => ({
          ...prev,
          [pathId]: progress
        }));
        router.push(`/learning-paths/${pathId}`);
      }
    } catch (error) {
      console.error("Failed to start path:", error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      beginner: "bg-green-100 text-green-800",
      intermediate: "bg-blue-100 text-blue-800",
      advanced: "bg-purple-100 text-purple-800",
      expert: "bg-red-100 text-red-800"
    };
    return colors[difficulty] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading learning paths...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <SectionHeading className="text-white">Learning Paths</SectionHeading>
            <p className="text-slate-300 text-lg mt-4 max-w-3xl">
              Follow structured learning paths to master new skills. Each path contains a sequence of carefully selected challenges designed to build your expertise from foundation to mastery.
            </p>
          </div>

          {/* Filters */}
          <div className="mb-8 flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedDifficulty("")}
              className={`px-4 py-2 rounded-full transition ${
                selectedDifficulty === ""
                  ? "bg-blue-600 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
            >
              All Levels
            </button>
            {["beginner", "intermediate", "advanced", "expert"].map(level => (
              <button
                key={level}
                onClick={() => setSelectedDifficulty(level)}
                className={`px-4 py-2 rounded-full transition capitalize ${
                  selectedDifficulty === level
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
              >
                {level}
              </button>
            ))}
          </div>

          {/* Paths Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPaths.length > 0 ? (
              filteredPaths.map(path => {
                const progress = userProgress[path.id];
                const isStarted = !!progress;
                
                return (
                  <Link key={path.id} href={`/learning-paths/${path.id}`}>
                    <Card className="h-full hover:shadow-lg hover:shadow-blue-500/20 cursor-pointer transition bg-slate-800 border-slate-700">
                      <div className="space-y-4">
                        {/* Icon & Badge */}
                        <div className="flex items-start justify-between">
                          <div className="text-4xl">{path.icon || "📚"}</div>
                          <span className={`text-xs font-semibold px-3 py-1 rounded-full capitalize ${getDifficultyColor(path.difficulty)}`}>
                            {path.difficulty}
                          </span>
                        </div>

                        {/* Title & Description */}
                        <div>
                          <h3 className="text-xl font-bold text-white mb-2">{path.title}</h3>
                          <p className="text-slate-400 text-sm line-clamp-2">{path.description}</p>
                        </div>

                        {/* Metadata */}
                        <div className="flex items-center justify-between text-sm text-slate-400 border-t border-slate-700 pt-4">
                          <div className="flex gap-4">
                            <span>⏱️ {path.estimated_hours}h</span>
                            <span>🎯 {path.total_challenges} challenges</span>
                          </div>
                        </div>

                        {/* Progress Bar (if started) */}
                        {isStarted && progress && (
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs text-slate-300">
                              <span>Progress</span>
                              <span>{progress.completion_percentage}%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all"
                                style={{ width: `${progress.completion_percentage}%` }}
                              />
                            </div>
                            <div className="text-xs text-slate-400">
                              {progress.completed_challenges}/{progress.total_challenges} completed
                            </div>
                          </div>
                        )}

                        {/* CTA Button */}
                        <div className="pt-4">
                          {isStarted && !progress.is_completed ? (
                            <Button variant="secondary" className="w-full">
                              Continue Learning
                            </Button>
                          ) : isStarted && progress.is_completed ? (
                            <button
                              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition"
                            >
                              ✓ Completed
                            </button>
                          ) : (
                            <Button 
                              className="w-full"
                              onClick={(e) => {
                                e.preventDefault();
                                startPath(path.id);
                              }}
                            >
                              Start Path
                            </Button>
                          )}
                        </div>
                      </div>
                    </Card>
                  </Link>
                );
              })
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-slate-400 text-lg">No learning paths found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
