import Head from 'next/head'
import Layout from '@/components/Layout'
import { PageHeader, PageContainer, PageSection, PageGrid, EmptyState, LoadingState } from '@/components/PageLayout'
import { StatCard, FeatureCard, ProgressCard, AlertCard, ActionCard } from '@/components/Cards'
import { Button } from '@/components/Button'

/**
 * UI Component Showcase
 * This page demonstrates all available UI components
 * Use this as a reference when building new pages
 */

export default function UIShowcase() {
  return (
    <Layout maxWidth="7xl">
      <Head>
        <title>UI Components - SkillForge Global</title>
      </Head>

      {/* Page Header with Actions */}
      <PageHeader
        icon="🎨"
        title="UI Component Library"
        subtitle="Consistent, beautiful components for building pages across the platform"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'UI Showcase' }
        ]}
        actions={
          <>
            <Button variant="secondary">Secondary Action</Button>
            <Button variant="primary">Primary Action</Button>
          </>
        }
      />

      {/* Alert Cards Section */}
      <PageSection
        icon="🔔"
        title="Alert Cards"
        subtitle="Use these for important notifications and messages"
      >
        <div className="space-y-4">
          <AlertCard
            variant="success"
            title="Success!"
            message="Your subscription has been upgraded to Pro plan."
            action={
              <Button variant="primary" size="sm">
                View Dashboard
              </Button>
            }
          />
          <AlertCard
            variant="warning"
            title="Action Required"
            message="Please complete your Stripe Connect onboarding to start receiving payouts."
            action={
              <Button variant="secondary" size="sm">
                Complete Onboarding
              </Button>
            }
            onDismiss={() => alert('Dismissed')}
          />
          <AlertCard
            variant="info"
            title="New Feature Available"
            message="We've added video call recording! You can now record your mentor sessions."
          />
        </div>
      </PageSection>

      {/* Stats Cards Section */}
      <PageSection
        icon="📊"
        title="Statistics Cards"
        subtitle="Display key metrics and numbers"
      >
        <PageGrid cols={4} gap="md">
          <StatCard
            icon="📚"
            label="Courses Completed"
            value="12"
            trend={{ value: 20, direction: 'up' }}
            href="/paths"
            color="purple"
          />
          <StatCard
            icon="🏆"
            label="Quiz Average"
            value="87%"
            trend={{ value: 5, direction: 'up' }}
            color="green"
          />
          <StatCard
            icon="🔥"
            label="Day Streak"
            value="15"
            color="orange"
          />
          <StatCard
            icon="💎"
            label="Forge Credits"
            value="450"
            href="/dashboard"
            color="blue"
          />
        </PageGrid>
      </PageSection>

      {/* Progress Cards Section */}
      <PageSection
        icon="📈"
        title="Progress Cards"
        subtitle="Show learning progress and course completion"
      >
        <PageGrid cols={2} gap="lg">
          <ProgressCard
            icon="🐍"
            title="Python AI Engineer"
            subtitle="Master machine learning with Python"
            progress={75}
            href="/paths/python-ai"
            stats={[
              { label: 'Videos', value: '45/60' },
              { label: 'Quizzes', value: '8/10' }
            ]}
          />
          <ProgressCard
            icon="⚛️"
            title="Full Stack Development"
            subtitle="Build modern web applications"
            progress={40}
            href="/paths/fullstack"
            stats={[
              { label: 'Videos', value: '24/60' },
              { label: 'Quizzes', value: '4/10' }
            ]}
          />
        </PageGrid>
      </PageSection>

      {/* Feature Cards Section */}
      <PageSection
        icon="✨"
        title="Feature Cards"
        subtitle="Highlight features and services"
      >
        <PageGrid cols={3} gap="md">
          <FeatureCard
            icon="👨‍🏫"
            title="Book a Mentor"
            description="Get personalized guidance from industry experts. 1-on-1 sessions with video calls."
            href="/mentors"
            badge="Popular"
          />
          <FeatureCard
            icon="🤖"
            title="AI Assistant"
            description="Get instant help with your coding questions using our advanced AI."
            href="/ai"
            badge="New"
          />
          <FeatureCard
            icon="💳"
            title="Upgrade to Pro"
            description="Unlock unlimited access, longer sessions, and premium features."
            href="/pricing"
          />
        </PageGrid>
      </PageSection>

      {/* Action Cards Section */}
      <PageSection
        icon="🚀"
        title="Action Cards"
        subtitle="Call-to-action cards with prominent buttons"
      >
        <PageGrid cols={2} gap="md">
          <ActionCard
            icon="🎓"
            title="Start Learning"
            description="Choose from 50+ career paths and start your journey today."
            buttonText="Browse Courses"
            buttonHref="/paths"
            variant="gradient"
          />
          <ActionCard
            icon="💰"
            title="Become a Mentor"
            description="Share your expertise and earn money helping others learn."
            buttonText="Apply Now"
            buttonHref="/mentors/become"
            variant="default"
          />
        </PageGrid>
      </PageSection>

      {/* Empty State Section */}
      <PageSection
        icon="📭"
        title="Empty States"
        subtitle="Show when there's no content available"
      >
        <PageContainer variant="card">
          <EmptyState
            icon="📚"
            title="No courses in progress"
            description="Start learning by choosing a career path that interests you."
            action={
              <Button variant="primary" size="lg">
                Browse Courses
              </Button>
            }
          />
        </PageContainer>
      </PageSection>

      {/* Loading State Section */}
      <PageSection
        icon="⏳"
        title="Loading States"
        subtitle="Display while content is being fetched"
      >
        <PageContainer variant="card">
          <LoadingState message="Loading your dashboard..." />
        </PageContainer>
      </PageSection>

      {/* Container Variants Section */}
      <PageSection
        icon="📦"
        title="Container Variants"
        subtitle="Different background styles for content sections"
      >
        <div className="space-y-6">
          <PageContainer variant="default">
            <h3 className="text-xl font-bold mb-2">Default Container</h3>
            <p className="text-white/60">No background, just content.</p>
          </PageContainer>

          <PageContainer variant="card">
            <h3 className="text-xl font-bold mb-2">Card Container</h3>
            <p className="text-white/60">Semi-transparent background with border.</p>
          </PageContainer>

          <PageContainer variant="glass">
            <h3 className="text-xl font-bold mb-2">Glass Container</h3>
            <p className="text-white/60">Premium glass morphism effect.</p>
          </PageContainer>
        </div>
      </PageSection>

      {/* Grid System Section */}
      <PageSection
        icon="🎯"
        title="Grid System"
        subtitle="Responsive grid layouts for organizing content"
      >
        <div className="space-y-8">
          <div>
            <h4 className="text-sm font-semibold text-white/60 mb-4">4 Columns (Stats)</h4>
            <PageGrid cols={4} gap="sm">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-white/5 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold">{i}</div>
                  <div className="text-sm text-white/60">Column {i}</div>
                </div>
              ))}
            </PageGrid>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white/60 mb-4">3 Columns (Features)</h4>
            <PageGrid cols={3} gap="md">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-white/5 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold">{i}</div>
                  <div className="text-sm text-white/60">Column {i}</div>
                </div>
              ))}
            </PageGrid>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white/60 mb-4">2 Columns (Content)</h4>
            <PageGrid cols={2} gap="lg">
              {[1, 2].map(i => (
                <div key={i} className="bg-white/5 rounded-lg p-6 text-center">
                  <div className="text-2xl font-bold">{i}</div>
                  <div className="text-sm text-white/60">Column {i}</div>
                </div>
              ))}
            </PageGrid>
          </div>
        </div>
      </PageSection>

      {/* Button Variants Section */}
      <PageSection
        icon="🔘"
        title="Button Variants"
        subtitle="All available button styles and sizes"
      >
        <PageContainer variant="card">
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold mb-3">Variants</h4>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Sizes</h4>
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="primary" size="sm">Small</Button>
                <Button variant="primary" size="md">Medium</Button>
                <Button variant="primary" size="lg">Large</Button>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Full Width</h4>
              <Button variant="primary" className="w-full">Full Width Button</Button>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Disabled State</h4>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary" disabled>Primary Disabled</Button>
                <Button variant="secondary" disabled>Secondary Disabled</Button>
              </div>
            </div>
          </div>
        </PageContainer>
      </PageSection>
    </Layout>
  )
}
