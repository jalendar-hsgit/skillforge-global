/**
 * Mentor search filters component
 * Provides advanced filtering by expertise, price, rating, and availability
 */

import React from 'react';

interface MentorFiltersProps {
  onFiltersChange: (filters: FilterState) => void;
  loading?: boolean;
}

export interface FilterState {
  query?: string;
  expertise?: string;
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
  availability?: boolean;
  sortBy?: string;
}

const expertiseOptions = [
  { value: 'python-ai', label: 'Python & AI' },
  { value: 'web-dev', label: 'Web Development' },
  { value: 'data-science', label: 'Data Science' },
  { value: 'cloud', label: 'Cloud & DevOps' },
  { value: 'mobile', label: 'Mobile Development' }
];

const sortOptions = [
  { value: 'name', label: 'Name (A-Z)' },
  { value: 'rating', label: 'Highest Rating' },
  { value: 'price', label: 'Lowest Price' },
  { value: 'newest', label: 'Newest First' }
];

export function MentorFilters({ onFiltersChange, loading }: MentorFiltersProps) {
  const [filters, setFilters] = React.useState<FilterState>({
    sortBy: 'name'
  });

  const [showAdvanced, setShowAdvanced] = React.useState(false);

  const handleChange = (newFilters: Partial<FilterState>) => {
    const updated = { ...filters, ...newFilters };
    setFilters(updated);
    onFiltersChange(updated);
  };

  const resetFilters = () => {
    const empty: FilterState = { sortBy: 'name' };
    setFilters(empty);
    onFiltersChange(empty);
  };

  return (
    <div className="space-y-4 p-4 bg-white rounded-lg border">
      {/* Search bar */}
      <div>
        <label className="block text-sm font-medium mb-2">Search Mentors</label>
        <input
          type="text"
          value={filters.query || ''}
          onChange={(e) => handleChange({ query: e.target.value || undefined })}
          placeholder="Name, expertise, or bio..."
          disabled={loading}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
      </div>

      {/* Sort */}
      <div>
        <label className="block text-sm font-medium mb-2">Sort By</label>
        <select
          value={filters.sortBy || 'name'}
          onChange={(e) => handleChange({ sortBy: e.target.value })}
          disabled={loading}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Toggle advanced filters */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-blue-600 hover:text-blue-700 text-sm font-medium"
      >
        {showAdvanced ? '− Hide Advanced Filters' : '+ Advanced Filters'}
      </button>

      {/* Advanced filters */}
      {showAdvanced && (
        <div className="space-y-4 pt-4 border-t">
          {/* Expertise */}
          <div>
            <label className="block text-sm font-medium mb-2">Expertise</label>
            <div className="space-y-2">
              {expertiseOptions.map((exp) => (
                <label key={exp.value} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={filters.expertise === exp.value}
                    onChange={(e) =>
                      handleChange({ expertise: e.target.checked ? exp.value : undefined })
                    }
                    disabled={loading}
                    className="rounded disabled:opacity-50"
                  />
                  <span className="text-sm">{exp.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Price range */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-2">Min Price ($/hr)</label>
              <input
                type="number"
                value={filters.minPrice || ''}
                onChange={(e) => handleChange({ minPrice: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="0"
                min="0"
                max="500"
                disabled={loading}
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Max Price ($/hr)</label>
              <input
                type="number"
                value={filters.maxPrice || ''}
                onChange={(e) => handleChange({ maxPrice: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="500"
                min="0"
                max="500"
                disabled={loading}
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
          </div>

          {/* Minimum rating */}
          <div>
            <label className="block text-sm font-medium mb-2">Minimum Rating</label>
            <select
              value={filters.minRating || ''}
              onChange={(e) => handleChange({ minRating: e.target.value ? Number(e.target.value) : undefined })}
              disabled={loading}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="">Any rating</option>
              <option value="4">4★ and up</option>
              <option value="4.5">4.5★ and up</option>
              <option value="5">5★ only</option>
            </select>
          </div>

          {/* Availability */}
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={filters.availability || false}
              onChange={(e) => handleChange({ availability: e.target.checked || undefined })}
              disabled={loading}
              className="rounded disabled:opacity-50"
            />
            <span className="text-sm">Show only available mentors</span>
          </label>

          {/* Reset button */}
          <button
            onClick={resetFilters}
            disabled={loading}
            className="w-full py-2 border text-gray-700 rounded-md hover:bg-gray-50 font-medium disabled:opacity-50"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
}
