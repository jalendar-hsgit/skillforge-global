import { APIRequestContext, BrowserContext } from '@playwright/test';

const BACKEND_BASE = process.env.E2E_BACKEND_BASE || 'http://127.0.0.1:8001';
const FRONTEND_DOMAIN = process.env.E2E_FRONTEND_DOMAIN || 'localhost';

let cachedToken: string | null = null;
let cachedEmail: string | null = null;

async function delay(ms: number) {
  return new Promise(res => setTimeout(res, ms));
}

export async function loginOnce(context: BrowserContext, request: APIRequestContext, email: string, password: string, fullName?: string) {
  if (cachedToken && cachedEmail === email) {
    await context.addCookies([
      { name: 'token', value: cachedToken, domain: FRONTEND_DOMAIN, path: '/', httpOnly: true, sameSite: 'Lax' },
    ]);
    return cachedToken;
  }

  // Best-effort signup
  try {
    await request.post(`${BACKEND_BASE}/api/v1/auth/signup`, {
      data: { email, password, full_name: fullName || 'E2E User' },
    });
  } catch {}

  // Exponential backoff for login to survive 429s
  const delays = [0, 2000, 5000, 8000, 12000];
  let lastError: any;
  for (const d of delays) {
    if (d) await delay(d);
    const resp = await request.post(`${BACKEND_BASE}/api/v1/auth/login`, {
      data: { email, password },
    });
    if (resp.ok()) {
      const setCookie = resp.headers()['set-cookie'] as unknown as string | undefined;
      if (setCookie && setCookie.includes('token=')) {
        const tokenMatch = setCookie.match(/token=([^;]+)/);
        if (tokenMatch) {
          cachedToken = tokenMatch[1];
          cachedEmail = email;
          await context.addCookies([
            { name: 'token', value: cachedToken, domain: FRONTEND_DOMAIN, path: '/', httpOnly: true, sameSite: 'Lax' },
          ]);
          return cachedToken;
        }
      }
      // If no cookie header but 200, try /me to fetch token later (fallback noop here)
      return '';
    } else {
      lastError = { status: resp.status(), body: await resp.text().catch(() => '') };
    }
  }
  throw new Error(`Login failed after retries: ${JSON.stringify(lastError)}`);
}
