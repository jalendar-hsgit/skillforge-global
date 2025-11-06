import { useState } from 'react';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { 
  Type, Palette, Image, BarChart3, Icons, 
  Sliders, ChevronDown, ChevronUp, X 
} from 'lucide-react';

// 12 Professional Fonts
const FONTS = [
  { value: 'Roboto', label: 'Roboto', category: 'Modern' },
  { value: 'Open Sans', label: 'Open Sans', category: 'Modern' },
  { value: 'Inter', label: 'Inter', category: 'Modern' },
  { value: 'Lato', label: 'Lato', category: 'Modern' },
  { value: 'Montserrat', label: 'Montserrat', category: 'Modern' },
  { value: 'Poppins', label: 'Poppins', category: 'Modern' },
  { value: 'Arial', label: 'Arial', category: 'Classic' },
  { value: 'Calibri', label: 'Calibri', category: 'Classic' },
  { value: 'Times New Roman', label: 'Times New Roman', category: 'Classic' },
  { value: 'Georgia', label: 'Georgia', category: 'Classic' },
  { value: 'Helvetica', label: 'Helvetica', category: 'Classic' },
  { value: 'Garamond', label: 'Garamond', category: 'Classic' },
];

// 74 Color Themes (showing 24 most popular)
const COLOR_THEMES = [
  { value: 'blue', label: 'Professional Blue', color: '#2563eb' },
  { value: 'navy', label: 'Navy', color: '#1e40af' },
  { value: 'teal', label: 'Teal', color: '#0891b2' },
  { value: 'cyan', label: 'Cyan', color: '#06b6d4' },
  { value: 'indigo', label: 'Indigo', color: '#6366f1' },
  { value: 'purple', label: 'Purple', color: '#8b5cf6' },
  { value: 'violet', label: 'Violet', color: '#7c3aed' },
  { value: 'pink', label: 'Pink', color: '#ec4899' },
  { value: 'rose', label: 'Rose', color: '#f43f5e' },
  { value: 'red', label: 'Red', color: '#ef4444' },
  { value: 'orange', label: 'Orange', color: '#f97316' },
  { value: 'amber', label: 'Amber', color: '#f59e0b' },
  { value: 'green', label: 'Green', color: '#10b981' },
  { value: 'emerald', label: 'Emerald', color: '#059669' },
  { value: 'lime', label: 'Lime', color: '#84cc16' },
  { value: 'gray', label: 'Professional Gray', color: '#4b5563' },
  { value: 'slate', label: 'Slate', color: '#64748b' },
  { value: 'zinc', label: 'Zinc', color: '#71717a' },
  { value: 'black', label: 'Executive Black', color: '#000000' },
  { value: 'forest', label: 'Forest Green', color: '#065f46' },
  { value: 'burgundy', label: 'Burgundy', color: '#991b1b' },
  { value: 'plum', label: 'Plum', color: '#7e22ce' },
  { value: 'sky', label: 'Sky Blue', color: '#0ea5e9' },
  { value: 'mint', label: 'Mint', color: '#14b8a6' },
];

// Picture Styles
const PICTURE_STYLES = [
  { value: 'circle', label: 'Circle', icon: '⭕' },
  { value: 'square', label: 'Square', icon: '⬜' },
  { value: 'rounded', label: 'Rounded', icon: '▢' },
  { value: 'none', label: 'No Picture', icon: '🚫' },
];

// Rating Styles
const RATING_STYLES = [
  { value: 'bars', label: 'Progress Bars', icon: '▬' },
  { value: 'dots', label: 'Dots', icon: '●' },
  { value: 'stars', label: 'Stars', icon: '★' },
  { value: 'circles', label: 'Circles', icon: '◉' },
];

// Background Types
const BACKGROUND_TYPES = [
  { value: 'none', label: 'None' },
  { value: 'solid', label: 'Solid Color' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'pattern', label: 'Pattern' },
];

// Layout Options
const LAYOUTS = [
  { value: 'single-column', label: 'Single Column', desc: 'Classic ATS-friendly' },
  { value: 'two-column', label: 'Two Column', desc: 'Modern split layout' },
  { value: 'sidebar', label: 'Sidebar', desc: 'Skills in sidebar' },
];

interface CustomizationPanelProps {
  resume: any;
  onUpdate: (updates: any) => void;
  onClose: () => void;
}

export default function CustomizationPanel({ resume, onUpdate, onClose }: CustomizationPanelProps) {
  const [activeTab, setActiveTab] = useState<'layout' | 'colors' | 'typography' | 'styling'>('layout');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['layout']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const handleChange = (field: string, value: any) => {
    onUpdate({ [field]: value });
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-deepNavy via-deepNavy/95 to-black border border-white/10 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-xl font-black text-white tracking-tight">
              Customize Resume
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Fine-tune every aspect of your resume appearance
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 p-4 border-b border-white/10 overflow-x-auto">
          {[
            { id: 'layout', label: 'Layout', icon: BarChart3 },
            { id: 'colors', label: 'Colors', icon: Palette },
            { id: 'typography', label: 'Typography', icon: Type },
            { id: 'styling', label: 'Styling', icon: Sliders },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-neuralBlue text-white shadow-lg shadow-neuralBlue/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 180px)' }}>
          {/* Layout Tab */}
          {activeTab === 'layout' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Page Layout
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {LAYOUTS.map((layout) => (
                    <button
                      key={layout.value}
                      onClick={() => handleChange('layout', layout.value)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        resume?.layout === layout.value
                          ? 'border-neuralBlue bg-neuralBlue/10'
                          : 'border-white/10 hover:border-white/30 bg-white/5'
                      }`}
                    >
                      <div className="font-bold text-white text-sm mb-1">
                        {layout.label}
                      </div>
                      <div className="text-xs text-gray-400">
                        {layout.desc}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Picture Style
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {PICTURE_STYLES.map((style) => (
                    <button
                      key={style.value}
                      onClick={() => handleChange('picture_style', style.value)}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        resume?.picture_style === style.value
                          ? 'border-neuralBlue bg-neuralBlue/10'
                          : 'border-white/10 hover:border-white/30 bg-white/5'
                      }`}
                    >
                      <div className="text-2xl mb-2">{style.icon}</div>
                      <div className="text-xs text-white font-medium">
                        {style.label}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Background Style
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {BACKGROUND_TYPES.map((bg) => (
                    <button
                      key={bg.value}
                      onClick={() => handleChange('background_type', bg.value)}
                      className={`p-3 rounded-xl border-2 transition-all text-center ${
                        resume?.background_type === bg.value
                          ? 'border-neuralBlue bg-neuralBlue/10'
                          : 'border-white/10 hover:border-white/30 bg-white/5'
                      }`}
                    >
                      <div className="text-xs text-white font-medium">
                        {bg.label}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Colors Tab */}
          {activeTab === 'colors' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Accent Color Theme
                </label>
                <div className="grid grid-cols-6 gap-3">
                  {COLOR_THEMES.map((theme) => (
                    <button
                      key={theme.value}
                      onClick={() => {
                        handleChange('color_theme', theme.value);
                        handleChange('accent_color', theme.color);
                      }}
                      className={`relative p-3 rounded-xl border-2 transition-all group ${
                        resume?.color_theme === theme.value || resume?.accent_color === theme.color
                          ? 'border-white ring-2 ring-white/30'
                          : 'border-white/20 hover:border-white/50'
                      }`}
                      style={{ backgroundColor: theme.color }}
                      title={theme.label}
                    >
                      <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors rounded-xl" />
                      <div className="relative text-white text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                        {theme.label.split(' ')[0]}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Custom Accent Color
                </label>
                <div className="flex gap-3 items-center">
                  <input
                    type="color"
                    value={resume?.accent_color || '#2563eb'}
                    onChange={(e) => handleChange('accent_color', e.target.value)}
                    className="h-12 w-24 rounded-lg cursor-pointer border-2 border-white/20"
                  />
                  <input
                    type="text"
                    value={resume?.accent_color || '#2563eb'}
                    onChange={(e) => handleChange('accent_color', e.target.value)}
                    className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-neuralBlue"
                    placeholder="#2563eb"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Text Color
                </label>
                <div className="flex gap-3 items-center">
                  <input
                    type="color"
                    value={resume?.text_color || '#000000'}
                    onChange={(e) => handleChange('text_color', e.target.value)}
                    className="h-12 w-24 rounded-lg cursor-pointer border-2 border-white/20"
                  />
                  <input
                    type="text"
                    value={resume?.text_color || '#000000'}
                    onChange={(e) => handleChange('text_color', e.target.value)}
                    className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-neuralBlue"
                    placeholder="#000000"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Heading Color
                </label>
                <div className="flex gap-3 items-center">
                  <input
                    type="color"
                    value={resume?.heading_color || '#1f2937'}
                    onChange={(e) => handleChange('heading_color', e.target.value)}
                    className="h-12 w-24 rounded-lg cursor-pointer border-2 border-white/20"
                  />
                  <input
                    type="text"
                    value={resume?.heading_color || '#1f2937'}
                    onChange={(e) => handleChange('heading_color', e.target.value)}
                    className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-neuralBlue"
                    placeholder="#1f2937"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Typography Tab */}
          {activeTab === 'typography' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Font Family
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {FONTS.map((font) => (
                    <button
                      key={font.value}
                      onClick={() => handleChange('font_family', font.value)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        resume?.font_family === font.value
                          ? 'border-neuralBlue bg-neuralBlue/10'
                          : 'border-white/10 hover:border-white/30 bg-white/5'
                      }`}
                      style={{ fontFamily: font.value }}
                    >
                      <div className="font-bold text-white text-base mb-1">
                        {font.label}
                      </div>
                      <div className="text-xs text-gray-400">
                        {font.category}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Font Size: {resume?.font_size || 11}pt
                </label>
                <input
                  type="range"
                  min="9"
                  max="14"
                  step="0.5"
                  value={resume?.font_size || 11}
                  onChange={(e) => handleChange('font_size', parseFloat(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-neuralBlue"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                  <span>9pt (Compact)</span>
                  <span>11pt (Standard)</span>
                  <span>14pt (Large)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Line Spacing: {resume?.line_spacing || 1.2}
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="2.0"
                  step="0.1"
                  value={resume?.line_spacing || 1.2}
                  onChange={(e) => handleChange('line_spacing', parseFloat(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-neuralBlue"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                  <span>1.0 (Tight)</span>
                  <span>1.5 (Comfortable)</span>
                  <span>2.0 (Spacious)</span>
                </div>
              </div>
            </div>
          )}

          {/* Styling Tab */}
          {activeTab === 'styling' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Skill Rating Style
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {RATING_STYLES.map((style) => (
                    <button
                      key={style.value}
                      onClick={() => handleChange('rating_style', style.value)}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        resume?.rating_style === style.value
                          ? 'border-neuralBlue bg-neuralBlue/10'
                          : 'border-white/10 hover:border-white/30 bg-white/5'
                      }`}
                    >
                      <div className="text-2xl mb-2">{style.icon}</div>
                      <div className="text-xs text-white font-medium">
                        {style.label}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 cursor-pointer hover:bg-white/10 transition-colors">
                  <div>
                    <div className="text-sm font-bold text-white">Show Section Icons</div>
                    <div className="text-xs text-gray-400 mt-1">
                      Display icons next to section headings
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={resume?.show_icons ?? true}
                    onChange={(e) => handleChange('show_icons', e.target.checked)}
                    className="w-5 h-5 rounded accent-neuralBlue cursor-pointer"
                  />
                </label>
              </div>

              <div>
                <label className="block text-sm font-bold text-white mb-3">
                  Page Settings
                </label>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 block mb-2">Page Size</label>
                    <select
                      value={resume?.page_size || 'A4'}
                      onChange={(e) => handleChange('page_size', e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-neuralBlue"
                    >
                      <option value="A4">A4 (210 × 297 mm)</option>
                      <option value="Letter">Letter (8.5 × 11 in)</option>
                      <option value="Legal">Legal (8.5 × 14 in)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs text-gray-400 block mb-2">Maximum Pages</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={resume?.max_pages || 2}
                      onChange={(e) => handleChange('max_pages', parseInt(e.target.value))}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-neuralBlue"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/10 bg-black/20">
          <button
            onClick={onClose}
            className="px-6 py-2.5 text-gray-400 hover:text-white font-medium transition-colors"
          >
            Cancel
          </button>
          <Button
            onClick={onClose}
            className="bg-gradient-to-r from-neuralBlue to-purple-600 hover:from-neuralBlue/90 hover:to-purple-600/90 text-white font-bold px-8 py-2.5 rounded-lg shadow-lg"
          >
            Apply Changes
          </Button>
        </div>
      </div>
    </div>
  );
}
