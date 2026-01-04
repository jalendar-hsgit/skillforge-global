import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Get token from Authorization header or cookies
    let token = req.headers.authorization?.replace("Bearer ", "");
    
    // If no token in Authorization header, try cookies
    if (!token && req.headers.cookie) {
      // Try to extract token from cookies
      const cookies = req.headers.cookie.split(';').map(c => c.trim());
      const tokenCookie = cookies.find(c => c.startsWith('token='));
      if (tokenCookie) {
        token = tokenCookie.replace('token=', '');
      }
    }

    if (!token) {
      return res.status(401).json({ detail: "Not authenticated" });
    }

    // Call backend with the token
    const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      return res.status(response.status).json({ detail: "Invalid token" });
    }

    const data = await response.json();
    
    return res.status(200).json({
      id: data.id,
      email: data.email,
      name: data.name || data.email?.split('@')[0],
      role: data.role || "USER",
    });
  } catch (error: any) {
    console.error("Session endpoint error:", error);
    res.status(500).json({ detail: error?.message || "Internal server error" });
  }
}

