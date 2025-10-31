"use client";

import { useRouter } from "next/router";
import { useEffect, useMemo, useState } from "react";

type Video = { id: number; title: string; youtube_id: string; duration: string };

export default function CourseVideosPage() {
  const router = useRouter();
  const { slug } = router.query as { slug?: string };

  const [videos, setVideos] = useState<Video[]>([]);
  const [q, setQ] = useState("");

  const title = useMemo(() => (slug ? slug.replaceAll("-", " ") : "Course"), [slug]);

  useEffect(() => {
    if (!router.isReady || !slug) return;
    fetch(`/api/courses/videos?slug=${encodeURIComponent(slug)}`)
      .then((r) => r.json())
      .then((j) => Array.isArray(j) ? setVideos(j) : setVideos([]))
      .catch(() => setVideos([]));
  }, [router.isReady, slug]);

  const filtered = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return videos;
    return videos.filter(v => v.title.toLowerCase().includes(t));
  }, [q, videos]);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-2xl font-semibold text-indigo-600 capitalize">{title} — Course Videos</h1>
        <div className="ml-auto w-64">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search videos…"
            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-xl border border-gray-200/70 bg-white p-6 text-gray-600">
          No videos found.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {filtered.map((v) => (
            <a
              key={v.id}
              href={`https://www.youtube.com/watch?v=${v.youtube_id}`}
              target="_blank"
              rel="noreferrer"
              className="group block bg-white rounded-xl border border-gray-200/70 shadow-sm hover:shadow transition overflow-hidden"
            >
              <img
                src={`https://i.ytimg.com/vi/${v.youtube_id}/hqdefault.jpg`}
                alt={v.title}
                className="w-full aspect-video object-cover"
              />
              <div className="p-3">
                <p className="text-sm font-medium text-gray-900 line-clamp-2 group-hover:text-indigo-600 transition">
                  {v.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">Duration: {v.duration}s</p>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
