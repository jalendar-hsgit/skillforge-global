import React, { useState } from 'react';

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'legendary';
  points: number;
  xp_reward?: number;
  coin_reward?: number;
  rarity?: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface UserAchievement {
  achievement: Achievement;
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
}

interface AchievementBadgeProps {
  achievement: UserAchievement;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'compact' | 'detailed' | 'showcase';
  showProgress?: boolean;
  showTooltip?: boolean;
  onClick?: () => void;
  className?: string;
}

// Rarity/Difficulty colors matching the theme
const rarityColors = {
  common: {
    border: 'border-gray-400',
    bg: 'from-gray-500/20 to-gray-600/20',
    glow: 'shadow-gray-400/20',
    text: 'text-gray-400',
    badge: 'bg-gray-500/30'
  },
  rare: {
    border: 'border-blue-400',
    bg: 'from-blue-500/20 to-blue-600/20',
    glow: 'shadow-blue-400/30',
    text: 'text-blue-400',
    badge: 'bg-blue-500/30'
  },
  epic: {
    border: 'border-purple-400',
    bg: 'from-purple-500/20 to-purple-600/20',
    glow: 'shadow-purple-400/40',
    text: 'text-purple-400',
    badge: 'bg-purple-500/30'
  },
  legendary: {
    border: 'border-yellow-400',
    bg: 'from-yellow-500/20 to-orange-600/20',
    glow: 'shadow-yellow-400/50',
    text: 'text-yellow-400',
    badge: 'bg-yellow-500/30'
  }
};

const difficultyToRarity = {
  easy: 'common',
  medium: 'rare',
  hard: 'epic',
  legendary: 'legendary'
} as const;

// Size configurations
const sizeConfig = {
  xs: { container: 'w-12 h-12', icon: 'text-xl', badge: 'w-16' },
  sm: { container: 'w-16 h-16', icon: 'text-2xl', badge: 'w-20' },
  md: { container: 'w-20 h-20', icon: 'text-3xl', badge: 'w-28' },
  lg: { container: 'w-24 h-24', icon: 'text-4xl', badge: 'w-32' },
  xl: { container: 'w-32 h-32', icon: 'text-5xl', badge: 'w-40' }
};

export const AchievementBadge: React.FC<AchievementBadgeProps> = ({
  achievement,
  size = 'md',
  variant = 'default',
  showProgress = true,
  showTooltip = true,
  onClick,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const { achievement: ach, unlockedAt, progress, maxProgress } = achievement;
  
  const isUnlocked = !!unlockedAt;
  const hasProgress = progress !== undefined && maxProgress !== undefined && maxProgress > 0;
  const progressPercent = hasProgress ? Math.min((progress / maxProgress) * 100, 100) : 0;
  
  const rarity = ach.rarity || difficultyToRarity[ach.difficulty] || 'common';
  const colors = rarityColors[rarity];
  const sizes = sizeConfig[size];
  
  const unlockedDate = unlockedAt ? new Date(unlockedAt).toLocaleDateString() : '';

  // Compact badge variant (just the icon)
  if (variant === 'compact') {
    return (
      <div 
        className={`relative group ${className}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={onClick}
      >
        <div
          className={`
            ${sizes.container} rounded-full flex items-center justify-center
            transition-all duration-300 cursor-pointer
            ${isUnlocked 
              ? `bg-gradient-to-br ${colors.bg} ${colors.border} border-2 shadow-lg ${colors.glow}` 
              : 'bg-white/5 border border-white/10 grayscale opacity-50'
            }
            ${isUnlocked ? 'hover:scale-110' : 'hover:opacity-70'}
          `}
        >
          <span className={`${sizes.icon} select-none ${!isUnlocked ? 'opacity-50' : ''}`}>
            {ach.icon}
          </span>
          {!isUnlocked && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-full">
              <span className="text-sm">🔒</span>
            </div>
          )}
        </div>
        
        {/* Tooltip */}
        {showTooltip && isHovered && (
          <Tooltip achievement={ach} isUnlocked={isUnlocked} unlockedDate={unlockedDate} colors={colors} rarity={rarity} />
        )}
      </div>
    );
  }

  // Showcase variant (large featured display)
  if (variant === 'showcase') {
    return (
      <div 
        className={`
          relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl
          rounded-2xl p-6 border ${isUnlocked ? colors.border : 'border-white/10'}
          ${isUnlocked ? `shadow-xl ${colors.glow}` : 'opacity-70'}
          transition-all duration-300 hover:scale-102
          ${onClick ? 'cursor-pointer' : ''}
          ${className}
        `}
        onClick={onClick}
      >
        {/* Rarity Ribbon */}
        <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${colors.badge} ${colors.text} uppercase`}>
          {rarity}
        </div>

        <div className="flex items-start gap-6">
          {/* Icon */}
          <div className={`
            w-24 h-24 rounded-xl flex items-center justify-center
            bg-gradient-to-br ${colors.bg} ${colors.border} border-2
            ${isUnlocked ? `shadow-lg ${colors.glow}` : 'grayscale opacity-50'}
          `}>
            <span className="text-5xl">{ach.icon}</span>
            {!isUnlocked && (
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl">🔒</span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-1">{ach.name}</h3>
            <p className="text-white/60 text-sm mb-3">{ach.description}</p>
            
            <div className="flex flex-wrap gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.badge} ${colors.text}`}>
                ⭐ {ach.points} Points
              </span>
              {ach.xp_reward && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-400">
                  +{ach.xp_reward} XP
                </span>
              )}
              {ach.coin_reward && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-yellow-500/20 text-yellow-400">
                  💰 {ach.coin_reward}
                </span>
              )}
            </div>

            {/* Progress */}
            {showProgress && hasProgress && !isUnlocked && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white/60">Progress</span>
                  <span className="text-white font-semibold">{progress}/{maxProgress}</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all duration-500`}
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>
            )}

            {/* Unlocked Date */}
            {isUnlocked && (
              <div className="mt-3 flex items-center gap-2 text-sm text-white/50">
                <span>✅ Unlocked</span>
                <span>•</span>
                <span>{unlockedDate}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Detailed variant (card with info)
  if (variant === 'detailed') {
    return (
      <div 
        className={`
          relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl
          rounded-xl p-4 border ${isUnlocked ? colors.border : 'border-white/10'}
          ${isUnlocked ? `shadow-lg ${colors.glow}` : 'opacity-70'}
          transition-all duration-300 hover:scale-105
          ${onClick ? 'cursor-pointer' : ''}
          ${className}
        `}
        onClick={onClick}
      >
        <div className="flex items-center gap-4">
          {/* Icon */}
          <div className={`
            ${sizes.container} rounded-xl flex items-center justify-center flex-shrink-0
            bg-gradient-to-br ${colors.bg} ${colors.border} border
            ${isUnlocked ? '' : 'grayscale opacity-50'}
          `}>
            <span className={sizes.icon}>{ach.icon}</span>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-bold text-white truncate">{ach.name}</h4>
              {isUnlocked && <span className="text-green-400">✓</span>}
            </div>
            <p className="text-white/50 text-sm line-clamp-1">{ach.description}</p>
            
            {/* Progress or Date */}
            {showProgress && hasProgress && !isUnlocked ? (
              <div className="mt-2">
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
                <span className="text-xs text-white/40 mt-1">{progress}/{maxProgress}</span>
              </div>
            ) : isUnlocked ? (
              <span className="text-xs text-white/40 mt-1">{unlockedDate}</span>
            ) : null}
          </div>

          {/* Points */}
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${colors.badge} ${colors.text}`}>
            +{ach.points}
          </div>
        </div>
      </div>
    );
  }

  // Default variant (badge with name)
  return (
    <div 
      className={`
        flex flex-col items-center gap-2 group relative
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      style={{ width: sizes.badge }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Badge Container */}
      <div className={`
        relative ${sizes.container} rounded-xl flex items-center justify-center
        transition-all duration-300
        ${isUnlocked 
          ? `bg-gradient-to-br ${colors.bg} ${colors.border} border-2 shadow-lg ${colors.glow}` 
          : 'bg-white/5 border border-white/10 grayscale opacity-50'
        }
        ${isUnlocked ? 'group-hover:scale-110 group-hover:shadow-xl' : 'group-hover:opacity-70'}
      `}>
        <span className={`${sizes.icon} select-none`}>{ach.icon}</span>
        
        {/* Lock Overlay */}
        {!isUnlocked && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-xl">
            <span className="text-base">🔒</span>
          </div>
        )}

        {/* Points Badge */}
        {isUnlocked && size !== 'xs' && (
          <div className={`absolute -top-1 -right-1 ${colors.badge} ${colors.text} text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center border border-white/20`}>
            +{ach.points}
          </div>
        )}
      </div>

      {/* Name */}
      <div className="text-center w-full">
        <h4 className={`font-semibold text-white line-clamp-2 ${size === 'xs' ? 'text-xs' : size === 'sm' ? 'text-xs' : 'text-sm'}`}>
          {ach.name}
        </h4>
        {size !== 'xs' && size !== 'sm' && (
          <span className={`text-xs ${colors.text} capitalize`}>{rarity}</span>
        )}
      </div>

      {/* Progress Bar */}
      {showProgress && hasProgress && !isUnlocked && size !== 'xs' && (
        <div className="w-full">
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-forgePurple to-neuralBlue transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <span className="text-xs text-white/40 block text-center mt-0.5">
            {progress}/{maxProgress}
          </span>
        </div>
      )}

      {/* Tooltip */}
      {showTooltip && isHovered && (
        <Tooltip achievement={ach} isUnlocked={isUnlocked} unlockedDate={unlockedDate} colors={colors} rarity={rarity} />
      )}
    </div>
  );
};

// Tooltip Component
const Tooltip: React.FC<{
  achievement: Achievement;
  isUnlocked: boolean;
  unlockedDate: string;
  colors: typeof rarityColors.common;
  rarity: string;
}> = ({ achievement, isUnlocked, unlockedDate, colors, rarity }) => (
  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 z-50 pointer-events-none">
    <div className="bg-gray-900/95 backdrop-blur-xl border border-white/20 rounded-xl p-3 shadow-2xl min-w-[200px] max-w-[280px]">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{achievement.icon}</span>
        <div>
          <h5 className="font-bold text-white text-sm">{achievement.name}</h5>
          <span className={`text-xs ${colors.text} capitalize`}>{rarity}</span>
        </div>
      </div>
      <p className="text-white/60 text-xs mb-2">{achievement.description}</p>
      <div className="flex flex-wrap gap-2 text-xs">
        <span className={`${colors.badge} ${colors.text} px-2 py-0.5 rounded-full`}>
          +{achievement.points} pts
        </span>
        {achievement.xp_reward && (
          <span className="bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
            +{achievement.xp_reward} XP
          </span>
        )}
      </div>
      {isUnlocked && (
        <div className="mt-2 pt-2 border-t border-white/10 text-xs text-green-400">
          ✅ Unlocked on {unlockedDate}
        </div>
      )}
    </div>
    {/* Arrow */}
    <div className="absolute left-1/2 transform -translate-x-1/2 -bottom-2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-gray-900/95" />
  </div>
);

// Achievement Grid Component for displaying multiple badges
interface AchievementGridProps {
  achievements: UserAchievement[];
  columns?: 2 | 3 | 4 | 5 | 6;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'compact' | 'detailed';
  showLocked?: boolean;
  onAchievementClick?: (achievement: UserAchievement) => void;
}

export const AchievementGrid: React.FC<AchievementGridProps> = ({
  achievements,
  columns = 4,
  size = 'md',
  variant = 'default',
  showLocked = true,
  onAchievementClick
}) => {
  const filteredAchievements = showLocked 
    ? achievements 
    : achievements.filter(a => a.unlockedAt);

  const gridCols = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4',
    5: 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5',
    6: 'grid-cols-3 sm:grid-cols-4 md:grid-cols-6'
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-4`}>
      {filteredAchievements.map((achievement) => (
        <AchievementBadge
          key={achievement.achievement.id}
          achievement={achievement}
          size={size}
          variant={variant}
          onClick={onAchievementClick ? () => onAchievementClick(achievement) : undefined}
        />
      ))}
    </div>
  );
};

// Achievement Stats Summary Component
interface AchievementStatsProps {
  totalAchievements: number;
  unlockedCount: number;
  totalPoints: number;
  recentUnlock?: UserAchievement;
}

export const AchievementStats: React.FC<AchievementStatsProps> = ({
  totalAchievements,
  unlockedCount,
  totalPoints,
  recentUnlock
}) => {
  const progressPercent = totalAchievements > 0 
    ? Math.round((unlockedCount / totalAchievements) * 100) 
    : 0;

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* Unlocked */}
        <div className="text-center">
          <div className="text-4xl font-bold text-white mb-1">{unlockedCount}</div>
          <div className="text-sm text-white/60">Unlocked</div>
        </div>

        {/* Total */}
        <div className="text-center">
          <div className="text-4xl font-bold text-white/50 mb-1">{totalAchievements}</div>
          <div className="text-sm text-white/60">Total</div>
        </div>

        {/* Points */}
        <div className="text-center">
          <div className="text-4xl font-bold text-yellow-400 mb-1">{totalPoints.toLocaleString()}</div>
          <div className="text-sm text-white/60">Points</div>
        </div>

        {/* Completion */}
        <div className="text-center">
          <div className="text-4xl font-bold text-green-400 mb-1">{progressPercent}%</div>
          <div className="text-sm text-white/60">Complete</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-6">
        <div className="h-3 bg-white/10 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-forgePurple via-neuralBlue to-green-400 transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Recent Unlock */}
      {recentUnlock && (
        <div className="mt-6 pt-6 border-t border-white/10">
          <div className="text-sm text-white/60 mb-2">Most Recent</div>
          <AchievementBadge 
            achievement={recentUnlock} 
            variant="detailed" 
            size="sm"
            showProgress={false}
          />
        </div>
      )}
    </div>
  );
};

export default AchievementBadge;
