import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }
  
  try {
    const { topic, difficulty, num_questions, options_per_question } = req.query;
    
    const params = new URLSearchParams({
      topic: String(topic || ''),
      difficulty: String(difficulty || 'medium'),
      num_questions: String(num_questions || '5'),
      options_per_question: String(options_per_question || '4')
    });
    
    const response = await fetch(`${API_BASE}/api/v1/quizzes/generate-stream?${params}`, {
      headers: {
        cookie: req.headers.cookie || "",
      },
      // @ts-ignore - Node.js fetch types
      credentials: 'include',
    });
    
    if (!response.ok) {
      const error = await response.text();
      res.status(response.status).json({ detail: error || 'Stream failed' });
      return;
    }
    
    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // Forward the stream
    const reader = response.body?.getReader();
    if (!reader) {
      res.status(500).json({ detail: 'No response body' });
      return;
    }
    
    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        res.write(chunk);
      }
    } finally {
      reader.releaseLock();
    }
    
    res.end();
  } catch (e: any) {
    console.error('Stream proxy error:', e);
    res.status(500).json({ detail: e.message || 'Stream error' });
  }
}
