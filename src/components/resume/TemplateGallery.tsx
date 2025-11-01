import { X, Check, FileText, Sparkles, Palette, Minimize2, Briefcase, Code, GraduationCap } from 'lucide-react';
import { useState } from 'react';

interface Template {
  id: string;
  name: string;
  description: string;
  icon: any;
  preview: string;
  features: string[];
  color: string;
}

interface TemplateGalleryProps {
  currentTemplate: string;
  onSelect: (templateId: string) => void;
  onClose: () => void;
}

const templates: Template[] = [
  {
    id: 'professional',
    name: 'Professional',
    description: 'Clean, ATS-friendly design perfect for corporate roles',
    icon: FileText,
    preview: '/templates/professional-preview.png',
    features: ['ATS Optimized', 'Corporate Friendly', 'Traditional Layout'],
    color: 'from-blue-500 to-blue-600',
  },
  {
    id: 'modern',
    name: 'Modern',
    description: 'Contemporary design with accent colors and visual hierarchy',
    icon: Sparkles,
    preview: '/templates/modern-preview.png',
    features: ['Eye-Catching', 'Color Accents', 'Modern Typography'],
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Bold layout for designers and creative professionals',
    icon: Palette,
    preview: '/templates/creative-preview.png',
    features: ['Unique Design', 'Portfolio Ready', 'Visual Impact'],
    color: 'from-orange-500 to-red-500',
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Simple, elegant design focusing on content over decoration',
    icon: Minimize2,
    preview: '/templates/minimal-preview.png',
    features: ['Clean Lines', 'Maximum Readability', 'Timeless Style'],
    color: 'from-gray-600 to-gray-700',
  },
    {
      id: 'executive',
      name: 'Executive',
      description: 'Premium serif design for senior leadership and C-suite roles',
      icon: Briefcase,
      preview: '/templates/executive-preview.png',
      features: ['Leadership Focus', 'Premium Feel', 'Bold Typography'],
      color: 'from-gray-800 to-gray-900',
    },
    {
      id: 'tech',
      name: 'Tech',
      description: 'Modern developer-focused layout with GitHub and portfolio emphasis',
      icon: Code,
      preview: '/templates/tech-preview.png',
      features: ['Dev-Friendly', 'Project Showcase', 'GitHub Ready'],
      color: 'from-blue-600 to-cyan-500',
    },
    {
      id: 'academic',
      name: 'Academic',
      description: 'Traditional research-oriented layout for academic positions',
      icon: GraduationCap,
      preview: '/templates/academic-preview.png',
      features: ['Publication Ready', 'Research Focus', 'Traditional'],
      color: 'from-indigo-600 to-purple-600',
    },
];

export default function TemplateGallery({ currentTemplate, onSelect, onClose }: TemplateGalleryProps) {
  const [hoveredTemplate, setHoveredTemplate] = useState<string | null>(null);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-md"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-gradient-to-br from-deepTech via-deepTech/95 to-deepTech/90 border-2 border-white/20 rounded-3xl shadow-2xl max-w-6xl w-full mx-6 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="relative px-8 py-6 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-black mb-2" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                <span className="bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent">
                  Choose Your Template
                </span>
              </h2>
              <p className="text-sm text-techGray/80 font-medium">
                  7 professional templates • Select one that matches your career goals
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-3 hover:bg-white/10 rounded-xl transition-all duration-200 group"
            >
              <X className="w-6 h-6 text-techGray group-hover:text-white transition-colors" />
            </button>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="p-8 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="grid grid-cols-2 gap-6">
            {templates.map((template) => {
              const Icon = template.icon;
              const isSelected = currentTemplate === template.id;
              const isHovered = hoveredTemplate === template.id;

              return (
                <div
                  key={template.id}
                  className={`group relative cursor-pointer transition-all duration-300 ${
                    isSelected ? 'scale-[1.02]' : 'hover:scale-[1.02]'
                  }`}
                  onMouseEnter={() => setHoveredTemplate(template.id)}
                  onMouseLeave={() => setHoveredTemplate(null)}
                  onClick={() => onSelect(template.id)}
                >
                  {/* Card */}
                  <div
                    className={`relative bg-white/5 border-3 rounded-2xl overflow-hidden transition-all duration-300 ${
                      isSelected
                        ? 'border-forgePurple shadow-2xl shadow-forgePurple/30'
                        : 'border-white/10 hover:border-white/30 hover:shadow-xl'
                    }`}
                  >
                    {/* Selected Badge */}
                    {isSelected && (
                      <div className="absolute top-4 right-4 z-10 px-4 py-2 bg-forgePurple rounded-xl flex items-center gap-2 shadow-lg">
                        <Check className="w-4 h-4 text-white" />
                        <span className="text-sm font-bold text-white">Selected</span>
                      </div>
                    )}

                    {/* Preview Area */}
                    <div className="relative aspect-[8.5/11] bg-gradient-to-br from-white/10 to-white/5 overflow-hidden">
                      {/* Icon Overlay */}
                      <div className={`absolute inset-0 flex items-center justify-center transition-opacity duration-300 ${
                        isHovered || isSelected ? 'opacity-100' : 'opacity-40'
                      }`}>
                        <div className={`p-6 bg-gradient-to-br ${template.color} rounded-2xl`}>
                          <Icon className="w-16 h-16 text-white" />
                        </div>
                      </div>

                      {/* Placeholder Grid Pattern */}
                      <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-8 left-8 right-8 h-4 bg-white/30 rounded"></div>
                        <div className="absolute top-16 left-8 right-24 h-2 bg-white/20 rounded"></div>
                        <div className="absolute top-20 left-8 right-16 h-2 bg-white/20 rounded"></div>
                        
                        <div className="absolute top-32 left-8 right-8 h-3 bg-white/30 rounded"></div>
                        <div className="absolute top-40 left-8 right-12 h-2 bg-white/15 rounded"></div>
                        <div className="absolute top-44 left-8 right-20 h-2 bg-white/15 rounded"></div>
                        <div className="absolute top-48 left-8 right-16 h-2 bg-white/15 rounded"></div>
                        
                        <div className="absolute top-60 left-8 right-8 h-3 bg-white/30 rounded"></div>
                        <div className="absolute top-68 left-8 right-16 h-2 bg-white/15 rounded"></div>
                        <div className="absolute top-72 left-8 right-24 h-2 bg-white/15 rounded"></div>
                      </div>
                    </div>

                    {/* Template Info */}
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-xl font-black text-white mb-1" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
                            {template.name}
                          </h3>
                          <p className="text-sm text-techGray/80 leading-relaxed">
                            {template.description}
                          </p>
                        </div>
                      </div>

                      {/* Features */}
                      <div className="flex flex-wrap gap-2">
                        {template.features.map((feature, index) => (
                          <span
                            key={index}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                              isSelected || isHovered
                                ? 'bg-forgePurple/20 border border-forgePurple/40 text-forgePurple'
                                : 'bg-white/10 border border-white/20 text-techGray'
                            }`}
                          >
                            {feature}
                          </span>
                        ))}
                      </div>

                      {/* Select Button */}
                      <button
                        className={`w-full mt-4 py-3 rounded-xl font-bold text-sm tracking-wide transition-all duration-300 ${
                          isSelected
                            ? 'bg-forgePurple text-white shadow-lg shadow-forgePurple/30'
                            : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                        }`}
                      >
                        {isSelected ? 'Currently Selected' : 'Use This Template'}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer Note */}
          <div className="mt-8 p-6 bg-neuralBlue/10 border border-neuralBlue/30 rounded-2xl">
            <p className="text-sm text-techGray/90 text-center font-medium leading-relaxed">
              💡 <strong className="text-white">Pro Tip:</strong> Professional and Minimal templates are best for ATS systems. 
              Choose Modern or Creative for roles that value design and creativity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
