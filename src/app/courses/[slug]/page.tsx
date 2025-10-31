"use client";

import { useState, useEffect } from "react";
import { apiGet } from "@/lib/api";

interface Video {
  id: number;
  title: string;
  youtube_id: string;
  duration: string;
}

export default function CoursePage({ params }: { params: { slug: string } }) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    apiGet(`/api/v1x/courses-db/${params.slug}/videos`)
      .then(setVideos)
      .catch(console.error);
  }, [params.slug]);

  const filtered = videos.filter(v =>
    v.title.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-indigo-600 mb-4 capitalize">
        {params.slug.replace("-", " ")} Course Videos
      </h1>
      <input
        type="text"
        placeholder="Search videos..."
        className="w-full border border-gray-300 rounded-lg p-2 mb-6 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {filtered.length === 0 ? (
        <p className="text-gray-500">No videos found.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {filtered.map((v) => (
            <a
              key={v.id}
              href={`https://www.youtube.com/watch?v=${v.youtube_id}`}
              target="_blank"
              rel="noreferrer"
              className="block bg-white rounded-xl shadow hover:shadow-md transition overflow-hidden"
            >
              <img
                src={`https://i.ytimg.com/vi/${v.youtube_id}/hqdefault.jpg`}
                alt={v.title}
                className="w-full aspect-video object-cover"
              />
              <div className="p-3">
                <p className="text-sm font-medium text-gray-800 line-clamp-2">
                  {v.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Duration: {v.duration}s
                </p>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
