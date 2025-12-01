import Head from 'next/head'
import Layout from '@/components/Layout'
import { Hero } from '@/components/Hero'
import CareerPathsGrid from '@/components/sections/CareerPathsGrid'
import FeaturedCourses from '@/components/sections/FeaturedCourses'
import SkillAIBridgeBand from '@/components/sections/SkillAIBridgeBand'
import Pricing from '@/components/sections/Pricing'
import FAQ from '@/components/sections/FAQ'
import { PageSection, PageGrid } from '@/components/PageLayout'
import { StatCard } from '@/components/Cards'

export default function HomePage() {
  return (
    <Layout maxWidth="7xl" showFooter={true}>
      <Head>
        <title>SkillForge Global – Forge your path to success</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <Hero />
      
      {/* Social Proof Stats */}
      <PageSection icon="📊" title="Join Thousands of Learners Worldwide">
        <PageGrid cols={4} gap="md">
          <StatCard
            icon="👥"
            label="Active Learners"
            value="50,000+"
            color="purple"
          />
          <StatCard
            icon="🎓"
            label="Courses Completed"
            value="125,000+"
            trend={{ value: 15, direction: 'up' }}
            color="blue"
          />
          <StatCard
            icon="💼"
            label="Career Transitions"
            value="12,500+"
            trend={{ value: 20, direction: 'up' }}
            color="green"
          />
          <StatCard
            icon="⭐"
            label="Average Rating"
            value="4.8/5"
            color="orange"
          />
        </PageGrid>
      </PageSection>
      
      <FeaturedCourses />
      <CareerPathsGrid />
      <SkillAIBridgeBand />
      <Pricing />
      <FAQ />
    </Layout>
  )
}
