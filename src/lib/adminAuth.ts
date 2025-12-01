import type { GetServerSidePropsContext } from 'next'

// Fetch current user using backend auth cookie and return user object or null
async function fetchMe(ctx: GetServerSidePropsContext) {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
  const cookie = ctx.req.headers.cookie || ''
  try {
    const res = await fetch(`${apiBase}/api/v1/auth/me`, {
      headers: { cookie },
    })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

export async function requireAdminSSR(ctx: GetServerSidePropsContext) {
  const me = await fetchMe(ctx)
  const role = me?.role?.toUpperCase()
  if (!me || !role || (role !== 'ADMIN' && role !== 'SUPERADMIN')) {
    return {
      redirect: {
        destination: `/login?redirect=${encodeURIComponent(ctx.resolvedUrl)}`,
        permanent: false,
      },
    }
  }
  return { props: { me } }
}

export type AdminSSRProps = { me: { id: number; email: string; role: string } }
