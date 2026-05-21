import React from 'react';

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  points: number;
}

export interface UserAchievement {
  achievement: Achievement;
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
}

interface AchievementCardProps {
  achievement: UserAchievement;
  size?: 'small' | 'medium' | 'large';
  showProgress?: boolean;
}

export const AchievementCard: React.FC<AchievementCardProps> = ({
  achievement,
  size = 'medium',
  showProgress = true
}) => {
  const { achievement: ach, unlockedAt, progress, maxProgress } = achievement;
  const isUnlocked = !!unlockedAt;
  const hasProgress = progress !== undefined && maxProgress !== undefined && maxProgress > 0;
  const progressPercent = hasProgress ? (progress / maxProgress) * 100 : 0;

  const sizeClasses = {
    small: 'w-24 h-24',
    medium: 'w-32 h-32',
    large: 'w-40 h-40'
  };

  const textSizeClasses = {
    small: 'text-3xl',
    medium: 'text-5xl',
    large: 'text-7xl'
  };

  const unlockedDate = unlockedAt ? new Date(unlockedAt).toLocaleDateString() : '';

  return (
    <div className={`flex flex-col items-center gap-2 ${sizeClasses[size]} group`}>
      {/* Achievement Card */}
      <div
        className={`relative w-full h-full rounded-lg border-2 flex items-center justify-center transition-all ${
          isUnlocked
            ? 'bg-gradient-to-br from-amber-100 to-amber-50 dark:from-amber-900 dark:to-amber-800 border-amber-300 dark:border-amber-600 shadow-lg'
            : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 shadow-sm grayscale opacity-60'
        }`}
      >
        {/* Icon */}
        <div className={`${textSizeClasses[size]} select-none`}>
          {ach.icon}
        </div>

        {/* Lock Icon for Locked Achievements */}
        {!isUnlocked && (
          <div className="absolute top-1 right-1 text-sm">🔒</div>
        )}

        {/* Points Badge */}
        {isUnlocked && (
          <div className="absolute top-1 right-1 bg-yellow-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
            +{ach.points}
          </div>
        )}

        {/* Unlock Date */}
        {isUnlocked && size !== 'small' && (
          <div className="absolute bottom-2 left-2 right-2 text-center">
            <span className="text-xs font-semibold text-amber-900 dark:text-amber-100">
              {unlockedDate}
            </span>
          </div>
        )}
      </div>

      {/* Achievement Name */}
      <div className="text-center w-full">
        <h3 className={`font-bold line-clamp-2 ${size === 'small' ? 'text-xs' : size === 'medium' ? 'text-sm' : 'text-base'}`}>
          {ach.name}
        </h3>

        {/* Progress Bar */}
        {showProgress && hasProgress && !isUnlocked && size !== 'small' && (
          <div className="mt-1 w-full">
            <div className="h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 dark:text-gray-400 mt-0.5 block">
              {progress}/{maxProgress}
            </span>
          </div>
        )}

        {/* Category Badge */}
        {size !== 'small' && (
          <div className="mt-1">
            <span className="inline-block text-xs bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 px-2 py-0.5 rounded-full capitalize">
              {ach.category}
            </span>
          </div>
        )}
      </div>

      {/* Hover Tooltip */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded py-1 px-2 whitespace-nowrap z-10">
        {ach.description}
      </div>
    </div>
  );
};

export default AchievementCard;
