import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState } from 'react'

type Msg = { role: 'user' | 'assistant', content: string }

export default function AIPage() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: 'assistant', content: 'Hi! I’m SkillAIBridge. What do you want to learn today?' }
  ])
  const [input, setInput] = useState('')

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text) return
    const next = [...messages, { role: 'user', content: text }]
    setMessages(next)
    setInput('')

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      setMessages([...next, { role: 'assistant', content: data.reply ?? 'OK' }])
    } catch (err) {
      setMessages([...next, { role: 'assistant', content: 'Server error. Try again.' }])
    }
  }

  return (
    <Layout>
      <Head><title>SkillAIBridge – AI Tutor</title></Head>
      <section className="mx-auto max-w-4xl px-6 pt-36 pb-10">
        <h1 className="text-3xl md:text-4xl font-semibold mb-2">SkillAIBridge</h1>
        <p className="text-techGray mb-6">Your AI mentor. Personalized roadmaps, instant feedback, and interview prep.</p>

        <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[60vh] flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {messages.map((m, i) => (
              <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
                <div className={`inline-block px-4 py-2 rounded-lg ${m.role === 'user' ? 'bg-forgePurple/30' : 'bg-neuralBlue/20'}`}>
                  {m.content}
                </div>
              </div>
            ))}
          </div>
          <form onSubmit={handleSend} className="mt-3 flex gap-2">
            <input
              className="flex-1 h-12 rounded-md bg-white/5 border border-white/10 px-4"
              placeholder="Ask a question or say what you want to learn…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button className="h-12 px-5 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue">Send</button>
          </form>
        </div>
      </section>
    </Layout>
  )
}
