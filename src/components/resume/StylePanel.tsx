import { useState } from 'react';
import { Palette, Type, Layout as LayoutIcon, Image, ChevronDown, ChevronUp } from 'lucide-react';

interface Resume {
  font_family?: string;
  font_size?: number;
  heading_size?: number;
  accent_color?: string;
  text_color?: string;
  heading_color?: string;
  layout?: string;
  picture_style?: string;
  show_icons?: boolean;
  line_spacing?: number;
  color_theme?: string;
}

interface StylePanelProps {
  resume: Resume;
  onUpdate: (updates: Partial<Resume>) => void;
}

const FONTS = [
  'Inter',
  'Roboto',
  'Open Sans',
  'Lato',
  'Montserrat',
  'Poppins',
  'Century Gothic',
  'Georgia',
  'Times New Roman',
  'Playfair Display',
  'Merriweather',
  'Courier New',
];

const LAYOUTS = [
  { value: 'modern', label: 'Modern' },
  { value: 'classic', label: 'Classic' },
  { value: 'minimal', label: 'Minimal' },
  { value: 'creative', label: 'Creative' },
  { value: 'beginner', label: 'Beginner (Centered)' },
  { value: 'two-column', label: 'Two Column' },
  { value: 'sidebar', label: 'Sidebar' },
];

const PICTURE_STYLES = [
  { value: 'none', label: 'No Picture' },
  { value: 'circle', label: 'Circle' },
  { value: 'square', label: 'Square' },
  { value: 'rounded', label: 'Rounded' },
];

const COLOR_PRESETS = [
  { name: 'Blue', value: '#2563eb' },
  { name: 'Purple', value: '#9333ea' },
  { name: 'Green', value: '#16a34a' },
  { name: 'Red', value: '#dc2626' },
  { name: 'Orange', value: '#ea580c' },
  { name: 'Teal', value: '#0d9488' },
  { name: 'Pink', value: '#db2777' },
  { name: 'Indigo', value: '#4f46e5' },
];

export default function StylePanel({ resume, onUpdate }: StylePanelProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    typography: true,
    colors: false,
    layout: false,
    advanced: false,
  });

  const toggleSection = (section: string) => {
    setExpanded(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const Section = ({ title, icon: Icon, name, children }: any) => (
    <div className="border border-white/10 rounded-lg overflow-hidden mb-3">
      <button
        onClick={() => toggleSection(name)}
        className="w-full flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-neuralBlue" />
          <span className="text-sm font-bold text-white">{title}</span>
        </div>
        {expanded[name] ? <ChevronUp className="w-4 h-4 text-techGray" /> : <ChevronDown className="w-4 h-4 text-techGray" />}
      </button>
      {expanded[name] && (
        <div className="p-4 space-y-4 bg-white/[0.02]">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-3">
      {/* Typography */}
      <Section title="Typography" icon={Type} name="typography">
        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Font Family</label>
          <select
            value={resume.font_family || 'Inter'}
            onChange={(e) => onUpdate({ font_family: e.target.value })}
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:border-neuralBlue focus:outline-none"
          >
            {FONTS.map(font => (
              <option key={font} value={font} className="bg-deepTech text-white">
                {font}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-techGray mb-2">Font Size (pt)</label>
            <input
              type="number"
              min="8"
              max="16"
              value={resume.font_size || 12}
              onChange={(e) => onUpdate({ font_size: parseInt(e.target.value) || 12 })}
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:border-neuralBlue focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-techGray mb-2">Heading Size (pt)</label>
            <input
              type="number"
              min="10"
              max="24"
              value={resume.heading_size || 14}
              onChange={(e) => onUpdate({ heading_size: parseInt(e.target.value) || 14 })}
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:border-neuralBlue focus:outline-none"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Line Spacing</label>
          <input
            type="range"
            min="1"
            max="2"
            step="0.1"
            value={resume.line_spacing || 1.2}
            onChange={(e) => onUpdate({ line_spacing: parseFloat(e.target.value) })}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-techGray mt-1">
            <span>Tight (1.0)</span>
            <span className="text-neuralBlue font-bold">{(resume.line_spacing || 1.2).toFixed(1)}</span>
            <span>Loose (2.0)</span>
          </div>
        </div>
      </Section>

      {/* Colors */}
      <Section title="Colors" icon={Palette} name="colors">
        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Accent Color</label>
          <div className="grid grid-cols-4 gap-2 mb-3">
            {COLOR_PRESETS.map(color => (
              <button
                key={color.value}
                onClick={() => onUpdate({ accent_color: color.value })}
                className={`h-10 rounded-lg border-2 transition-all ${
                  resume.accent_color === color.value
                    ? 'border-white scale-110 shadow-lg'
                    : 'border-white/20 hover:border-white/40'
                }`}
                style={{ backgroundColor: color.value }}
                title={color.name}
              />
            ))}
          </div>
          <input
            type="color"
            value={resume.accent_color || '#2563eb'}
            onChange={(e) => onUpdate({ accent_color: e.target.value })}
            className="w-full h-10 rounded-lg border border-white/10 bg-white/5 cursor-pointer"
          />
          <p className="text-xs text-techGray mt-1">Custom: {resume.accent_color || '#2563eb'}</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-techGray mb-2">Text Color</label>
            <input
              type="color"
              value={resume.text_color || '#000000'}
              onChange={(e) => onUpdate({ text_color: e.target.value })}
              className="w-full h-10 rounded-lg border border-white/10 bg-white/5 cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-techGray mb-2">Heading Color</label>
            <input
              type="color"
              value={resume.heading_color || '#1f2937'}
              onChange={(e) => onUpdate({ heading_color: e.target.value })}
              className="w-full h-10 rounded-lg border border-white/10 bg-white/5 cursor-pointer"
            />
          </div>
        </div>
      </Section>

      {/* Layout */}
      <Section title="Layout & Picture" icon={LayoutIcon} name="layout">
        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Layout Style</label>
          <select
            value={resume.layout || 'modern'}
            onChange={(e) => onUpdate({ layout: e.target.value })}
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:border-neuralBlue focus:outline-none"
          >
            {LAYOUTS.map(layout => (
              <option key={layout.value} value={layout.value} className="bg-deepTech text-white">
                {layout.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Picture Style</label>
          <div className="grid grid-cols-2 gap-2">
            {PICTURE_STYLES.map(style => (
              <button
                key={style.value}
                onClick={() => onUpdate({ picture_style: style.value })}
                className={`px-3 py-2 rounded-lg border text-sm transition-all ${
                  resume.picture_style === style.value
                    ? 'bg-neuralBlue/20 border-neuralBlue text-neuralBlue font-bold'
                    : 'bg-white/5 border-white/10 text-techGray hover:border-white/30'
                }`}
              >
                {style.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={resume.show_icons ?? true}
              onChange={(e) => onUpdate({ show_icons: e.target.checked })}
              className="w-4 h-4 rounded border-white/20 bg-white/5 checked:bg-neuralBlue cursor-pointer"
            />
            <span className="text-sm text-white">Show contact icons</span>
          </label>
        </div>
      </Section>

      {/* Advanced */}
      <Section title="Advanced" icon={Image} name="advanced">
        <div>
          <label className="block text-xs font-medium text-techGray mb-2">Color Theme</label>
          <input
            type="text"
            value={resume.color_theme || 'blue'}
            onChange={(e) => onUpdate({ color_theme: e.target.value })}
            placeholder="e.g., blue, purple, green"
            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:border-neuralBlue focus:outline-none"
          />
          <p className="text-xs text-techGray mt-1">
            Theme name for preset color palettes
          </p>
        </div>
      </Section>
    </div>
  );
}
