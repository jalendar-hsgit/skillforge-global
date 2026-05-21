import { useState } from 'react';
import { ChevronDown, Filter } from 'lucide-react';

interface FilterOption {
  value: string;
  label: string;
  count?: number;
}

interface FilterSidebarProps {
  categories?: FilterOption[];
  productTypes?: FilterOption[];
  onFilterChange?: (filters: FilterState) => void;
  loading?: boolean;
}

interface FilterState {
  category?: string;
  productType?: string;
  priceMin?: number;
  priceMax?: number;
  ratingMin?: number;
  sortBy?: string;
  verifiedOnly?: boolean;
}

export default function FilterSidebar({
  categories = [],
  productTypes = [],
  onFilterChange,
  loading = false
}: FilterSidebarProps) {
  const [filters, setFilters] = useState<FilterState>({
    sortBy: 'relevance',
    verifiedOnly: false
  });
  
  const [expandedSections, setExpandedSections] = useState({
    price: true,
    rating: true,
    category: true,
    type: true,
    sort: true
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleFilterChange = (newFilters: FilterState) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFilterChange?.(updatedFilters);
  };

  const handleReset = () => {
    const resetFilters = {
      sortBy: 'relevance',
      verifiedOnly: false
    };
    setFilters(resetFilters);
    onFilterChange?.(resetFilters);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-4 max-h-fit">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Filter size={18} />
          Filters
        </h3>
        <button
          onClick={handleReset}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Reset
        </button>
      </div>

      <div className="space-y-4">
        {/* Sort By */}
        <div className="border-b border-gray-200 pb-4">
          <button
            onClick={() => toggleSection('sort')}
            className="flex items-center justify-between w-full font-medium text-gray-900 hover:text-blue-600"
          >
            <span>Sort By</span>
            <ChevronDown
              size={18}
              className={`transition-transform ${expandedSections.sort ? 'rotate-180' : ''}`}
            />
          </button>
          {expandedSections.sort && (
            <div className="mt-3 space-y-2">
              {[
                { value: 'relevance', label: 'Most Relevant' },
                { value: 'price_low', label: 'Price: Low to High' },
                { value: 'price_high', label: 'Price: High to Low' },
                { value: 'newest', label: 'Newest First' },
                { value: 'popular', label: 'Most Popular' },
                { value: 'rating', label: 'Highest Rated' }
              ].map(option => (
                <label key={option.value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="sort"
                    value={option.value}
                    checked={filters.sortBy === option.value}
                    onChange={e => handleFilterChange({ ...filters, sortBy: e.target.value })}
                    disabled={loading}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">{option.label}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Price Range */}
        <div className="border-b border-gray-200 pb-4">
          <button
            onClick={() => toggleSection('price')}
            className="flex items-center justify-between w-full font-medium text-gray-900 hover:text-blue-600"
          >
            <span>Price</span>
            <ChevronDown
              size={18}
              className={`transition-transform ${expandedSections.price ? 'rotate-180' : ''}`}
            />
          </button>
          {expandedSections.price && (
            <div className="mt-3 space-y-3">
              <div>
                <label className="text-sm text-gray-600 block mb-1">Min Price</label>
                <input
                  type="number"
                  min="0"
                  value={filters.priceMin || ''}
                  onChange={e => handleFilterChange({
                    ...filters,
                    priceMin: e.target.value ? parseFloat(e.target.value) : undefined
                  })}
                  placeholder="$0"
                  disabled={loading}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="text-sm text-gray-600 block mb-1">Max Price</label>
                <input
                  type="number"
                  min="0"
                  value={filters.priceMax || ''}
                  onChange={e => handleFilterChange({
                    ...filters,
                    priceMax: e.target.value ? parseFloat(e.target.value) : undefined
                  })}
                  placeholder="$1000"
                  disabled={loading}
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Rating */}
        <div className="border-b border-gray-200 pb-4">
          <button
            onClick={() => toggleSection('rating')}
            className="flex items-center justify-between w-full font-medium text-gray-900 hover:text-blue-600"
          >
            <span>Rating</span>
            <ChevronDown
              size={18}
              className={`transition-transform ${expandedSections.rating ? 'rotate-180' : ''}`}
            />
          </button>
          {expandedSections.rating && (
            <div className="mt-3 space-y-2">
              {[5, 4, 3, 2, 1].map(rating => (
                <label key={rating} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="rating"
                    value={rating}
                    checked={filters.ratingMin === rating}
                    onChange={e => handleFilterChange({
                      ...filters,
                      ratingMin: parseFloat(e.target.value)
                    })}
                    disabled={loading}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">
                    {rating}★ & up {rating === 5 && '(Perfect)'}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Categories */}
        {categories.length > 0 && (
          <div className="border-b border-gray-200 pb-4">
            <button
              onClick={() => toggleSection('category')}
              className="flex items-center justify-between w-full font-medium text-gray-900 hover:text-blue-600"
            >
              <span>Category</span>
              <ChevronDown
                size={18}
                className={`transition-transform ${expandedSections.category ? 'rotate-180' : ''}`}
              />
            </button>
            {expandedSections.category && (
              <div className="mt-3 space-y-2">
                {categories.map(category => (
                  <label key={category.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.category === category.value}
                      onChange={e => handleFilterChange({
                        ...filters,
                        category: e.target.checked ? category.value : undefined
                      })}
                      disabled={loading}
                      className="w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">{category.label}</span>
                    {category.count !== undefined && (
                      <span className="text-xs text-gray-500">({category.count})</span>
                    )}
                  </label>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Product Type */}
        {productTypes.length > 0 && (
          <div className="border-b border-gray-200 pb-4">
            <button
              onClick={() => toggleSection('type')}
              className="flex items-center justify-between w-full font-medium text-gray-900 hover:text-blue-600"
            >
              <span>Type</span>
              <ChevronDown
                size={18}
                className={`transition-transform ${expandedSections.type ? 'rotate-180' : ''}`}
              />
            </button>
            {expandedSections.type && (
              <div className="mt-3 space-y-2">
                {productTypes.map(type => (
                  <label key={type.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.productType === type.value}
                      onChange={e => handleFilterChange({
                        ...filters,
                        productType: e.target.checked ? type.value : undefined
                      })}
                      disabled={loading}
                      className="w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">{type.label}</span>
                    {type.count !== undefined && (
                      <span className="text-xs text-gray-500">({type.count})</span>
                    )}
                  </label>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Verified Reviews Only */}
        <div className="pt-2">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.verifiedOnly || false}
              onChange={e => handleFilterChange({
                ...filters,
                verifiedOnly: e.target.checked
              })}
              disabled={loading}
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-700">Only verified reviews</span>
          </label>
        </div>
      </div>
    </div>
  );
}
