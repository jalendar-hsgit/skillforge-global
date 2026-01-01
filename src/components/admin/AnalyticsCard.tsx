import React from 'react';

interface AnalyticsCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    percentage: number;
    period: string;
  };
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
}

const colorClasses = {
  blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
  green: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
  red: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
  yellow: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
  purple: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800'
};

const valueColorClasses = {
  blue: 'text-blue-700 dark:text-blue-300',
  green: 'text-green-700 dark:text-green-300',
  red: 'text-red-700 dark:text-red-300',
  yellow: 'text-yellow-700 dark:text-yellow-300',
  purple: 'text-purple-700 dark:text-purple-300'
};

const getTrendColor = (direction: 'up' | 'down' | 'neutral') => {
  switch (direction) {
    case 'up': return 'text-green-600 dark:text-green-400';
    case 'down': return 'text-red-600 dark:text-red-400';
    default: return 'text-gray-600 dark:text-gray-400';
  }
};

const getTrendIcon = (direction: 'up' | 'down' | 'neutral') => {
  switch (direction) {
    case 'up': return '📈';
    case 'down': return '📉';
    default: return '➡️';
  }
};

const sizeClasses = {
  small: 'p-4',
  medium: 'p-6',
  large: 'p-8'
};

export const AnalyticsCard: React.FC<AnalyticsCardProps> = ({
  title,
  value,
  subtext,
  icon,
  trend,
  color = 'blue',
  size = 'medium',
  onClick
}) => {
  return (
    <div
      onClick={onClick}
      className={`rounded-lg border-2 ${colorClasses[color]} ${sizeClasses[size]} ${
        onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {title}
        </h3>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>

      <div className="mb-3">
        <p className={`text-3xl font-bold ${valueColorClasses[color]}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {subtext && (
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {subtext}
          </p>
        )}
      </div>

      {trend && (
        <div className={`flex items-center gap-2 text-sm font-semibold ${getTrendColor(trend.direction)}`}>
          <span>{getTrendIcon(trend.direction)}</span>
          <span>
            {trend.direction === 'down' ? '−' : '+'}
            {trend.percentage}% {trend.period}
          </span>
        </div>
      )}
    </div>
  );
};

export default AnalyticsCard;
