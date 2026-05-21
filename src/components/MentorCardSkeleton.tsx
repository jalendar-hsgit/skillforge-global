import React from 'react';
import { Card } from './Card';

export function MentorCardSkeleton() {
  return (
    <Card className="bg-glass backdrop-blur-xl border border-white/10 shadow-glass animate-pulse">
      <div className="space-y-4">
        {/* Avatar & Name */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-white/10 rounded-full"></div>
          <div className="flex-1">
            <div className="h-6 bg-white/10 rounded w-32 mb-2"></div>
            <div className="h-4 bg-white/10 rounded w-20"></div>
          </div>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="w-5 h-5 bg-white/10 rounded"></div>
            ))}
          </div>
          <div className="h-4 bg-white/10 rounded w-16"></div>
        </div>

        {/* Bio */}
        <div className="space-y-2">
          <div className="h-4 bg-white/10 rounded"></div>
          <div className="h-4 bg-white/10 rounded w-5/6"></div>
          <div className="h-4 bg-white/10 rounded w-4/6"></div>
        </div>

        {/* Expertise Tags */}
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-8 w-20 bg-white/10 rounded-full"></div>
          ))}
        </div>

        {/* Sessions Count */}
        <div className="pt-4 border-t border-white/10">
          <div className="h-4 bg-white/10 rounded w-32"></div>
        </div>

        {/* Button */}
        <div className="h-10 bg-white/10 rounded-lg"></div>
      </div>
    </Card>
  );
}
