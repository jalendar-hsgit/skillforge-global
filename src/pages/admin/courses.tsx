import Head from 'next/head'
import Layout from '@/components/Layout'
import { useState, useEffect } from 'react'

type Item = { id:string; path:string; title:string; youtubeId:string; duration?:string }

export default function AdminCourses() {
  const [items, setItems] = useState<Item[]>([])
  const [form, setForm] = useState<Item>({ id:'', path:'python-ai', title:'', youtubeId:'', duration:'' })
  const [adminKey, setAdminKey] = useState<string>('')

  useEffect(() => {
    const k = localStorage.getItem('ADMIN_KEY') || ''
    setAdminKey(k)
    load('python-ai')
  }, [])

  async function load(path: string) {
    const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/courses?path=${path}`)
    const d = await r.json()
    setItems(d)
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    localStorage.setItem('ADMIN_KEY', adminKey)
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/courses`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Key': adminKey
      },
      body: JSON.stringify(form)
    })
    if (!res.ok) {
      alert('Failed to add: ' + await res.text())
      return
    }
    const ok = await res.json()
    alert('Added!')
    setForm({ id:'', path:form.path, title:'', youtubeId:'', duration:'' })
    load(form.path)
  }

  return (
    <Layout>
      <Head><title>{`Admin – Courses`}</title></Head>
      <section className="mx-auto max-w-5xl px-6 pt-36 pb-20">
        <h1 className="text-2xl font-semibold mb-4">Admin – Add Course Video</h1>
        <form onSubmit={onSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
          <input className="h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Admin Key" value={adminKey} onChange={(e)=>setAdminKey(e.target.value)} />
          <select className="h-12 rounded-md bg-white/5 border border-white/10 px-4" value={form.path} onChange={(e)=>setForm({...form, path:e.target.value})}>
            <option value="python-ai">python-ai</option>
            <option value="fullstack">fullstack</option>
            <option value="aws-devops">aws-devops</option>
            <option value="cybersec">cybersec</option>
            <option value="flutter">flutter</option>
          </select>
          <input className="h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="ID (unique)" value={form.id} onChange={(e)=>setForm({...form, id:e.target.value})} required />
          <input className="h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Title" value={form.title} onChange={(e)=>setForm({...form, title:e.target.value})} required />
          <input className="h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="YouTube ID (e.g. rfscVS0vtbw)" value={form.youtubeId} onChange={(e)=>setForm({...form, youtubeId:e.target.value})} required />
          <input className="h-12 rounded-md bg-white/5 border border-white/10 px-4" placeholder="Duration (e.g. 1h30m)" value={form.duration} onChange={(e)=>setForm({...form, duration:e.target.value})} />
          <button className="h-12 rounded-md bg-gradient-to-r from-forgePurple to-neuralBlue px-6 font-semibold">Add</button>
        </form>

        <h2 className="text-xl font-semibold mb-2">Current items ({items.length})</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map(i => (
            <div key={i.id} className="rounded-xl border border-white/10 p-4 bg-white/[0.06]">
              <div className="text-sm font-semibold">{i.title}</div>
              <div className="text-xs text-techGray mt-1">{i.path} · {i.youtubeId} · {i.duration}</div>
            </div>
          ))}
        </div>
      </section>
    </Layout>
  )
}
