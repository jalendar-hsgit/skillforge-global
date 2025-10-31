export const ROUTES = {
  home: '/',
  login: '/login',
  signup: '/signup',
  dashboard: '/dashboard',
  career: '/careers',   // matches your existing page: src/pages/careers.tsx
  courses: '/courses',
  ai: '/ai',
  faq: '/faq',
  paths: '/paths',
  pricing: '/pricing',
  logout: '/logout',
  quiz: (slug?: string | null) => slug ? `/quiz/${slug}` : '/paths',
  path: (slug?: string | null) => slug ? `/paths/${slug}` : '/paths',
};
