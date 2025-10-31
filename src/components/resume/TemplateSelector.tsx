import { Card } from '@/components/Card'
import { Button } from '@/components/Button'

interface TemplateSelectorProps {
  currentTemplate: string
  onSelect: (template: string) => void
  onClose: () => void
}

const templates = [
  { key: 'modern', name: 'Modern', desc: 'Clean sans-serif with subtle accents' },
  { key: 'classic', name: 'Classic', desc: 'Serif typography with separators' },
  { key: 'minimal', name: 'Minimal', desc: 'Whitespace-first, airy layout' },
  { key: 'creative', name: 'Creative', desc: 'Colorful header and highlights' },
]

export default function TemplateSelector({ currentTemplate, onSelect, onClose }: TemplateSelectorProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <Card className="w-full max-w-3xl p-6 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">Choose a Template</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {templates.map(t => (
            <button
              key={t.key}
              onClick={() => onSelect(t.key)}
              className={`text-left p-4 border rounded-lg hover:shadow-md transition ${
                currentTemplate === t.key ? 'border-blue-500 ring-1 ring-blue-200' : 'border-gray-200'
              }`}
            >
              <div className="font-semibold text-gray-900">{t.name}</div>
              <div className="text-sm text-gray-600">{t.desc}</div>
              <div className="mt-3 h-24 rounded-md bg-gray-50 border border-dashed flex items-center justify-center text-xs text-gray-400">
                Preview
              </div>
            </button>
          ))}
        </div>
        <div className="mt-6 flex justify-end">
          <Button onClick={onClose} variant="secondary">Close</Button>
        </div>
      </Card>
    </div>
  )
}
