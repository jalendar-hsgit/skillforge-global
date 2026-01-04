import { NextRequest, NextResponse } from 'next/server'

// Routes that require authentication
const PROTECTED_ROUTES = [
  '/marketplace/seller',
  '/marketplace/seller/create-product',
  '/marketplace/seller/products',
  '/marketplace/seller/orders',
  '/marketplace/seller/analytics',
  '/dashboard',
  '/mentor',
  '/mentor/',
  '/mentor/dashboard',
]

// Routes that require seller role
const SELLER_ROUTES = [
  '/marketplace/seller',
  '/marketplace/seller/create-product',
  '/marketplace/seller/products',
  '/marketplace/seller/orders',
  '/marketplace/seller/analytics',
]

// Routes that require admin role
const ADMIN_ROUTES = [
  '/admin',
  '/admin/dashboard',
  '/admin/users',
  '/admin/analytics',
]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for static files and api routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname.startsWith('/public') ||
    pathname.startsWith('/api') ||
    pathname.match(/\.(png|jpg|jpeg|gif|svg|ico|webp)$/)
  ) {
    return NextResponse.next()
  }

  // Check if route is protected
  const isProtectedRoute = PROTECTED_ROUTES.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  )

  if (!isProtectedRoute) {
    return NextResponse.next()
  }

  // Get session from request
  // Note: In Next.js 13+, we check session via a header or cookie
  // The actual session validation will happen in the page component
  // But we can do initial checks here

  const isSeller = SELLER_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  )

  const isAdmin = ADMIN_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  )

  // If it's a seller route, redirect to login if no token
  if (isSeller) {
    const token = request.cookies.get('token')?.value
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  // If it's an admin route, redirect to login if no token
  if (isAdmin) {
    const token = request.cookies.get('token')?.value
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Match all routes except static files
    '/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)',
  ],
}
