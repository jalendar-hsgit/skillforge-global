import { useState, useEffect } from 'react'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  language: string
  height?: string
}

export default function CodeEditor({ value, onChange, language, height = '100%' }: CodeEditorProps) {
  return (
    <div className="h-full w-full bg-[#1e1e1e]" style={{ height }}>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-full bg-[#1e1e1e] text-gray-100 font-mono text-sm p-4 focus:outline-none resize-none"
        style={{
          tabSize: 2,
          fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace",
          lineHeight: '1.6'
        }}
        spellCheck={false}
        autoComplete="off"
        autoCorrect="off"
        autoCapitalize="off"
      />
    </div>
  )
}
