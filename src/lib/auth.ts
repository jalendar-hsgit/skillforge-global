/**
 * Server-side authentication guard for pages
 * Usage: export const getServerSideProps = requireAuthSSR()
 */

import type { GetServerSideProps } from 'next'

export const requireAuthSSR = (): GetServerSideProps => {
  return async (ctx) => {
    const base = `http://${ctx.req.headers.host}`
    try {
      const r = await fetch(`${base}/api/session/me`, {
        headers: { cookie: ctx.req.headers.cookie || '' }
      })
      if (!r.ok) {
        return { redirect: { destination: '/login', permanent: false } }
      }
      return { props: {} }
    } catch (error) {
      return { redirect: { destination: '/login', permanent: false } }
    }
  }
}

export const requireAdminSSR = (): GetServerSideProps => {
  return async (ctx) => {
    const base = `http://${ctx.req.headers.host}`
    try {
      const r = await fetch(`${base}/api/session/me`, {
        headers: { cookie: ctx.req.headers.cookie || '' }
      })
      if (!r.ok) {
        return { redirect: { destination: '/login', permanent: false } }
      }
      
      const user = await r.json()
      if (!user || (user.role !== 'ADMIN' && user.role !== 'SUPERADMIN')) {
        return { redirect: { destination: '/unauthorized', permanent: false } }
      }
      
      return { props: {} }
    } catch (error) {
      return { redirect: { destination: '/login', permanent: false } }
    }
  }
}
