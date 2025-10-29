import Head from 'next/head'
import Layout from '@/components/Layout'
import { Hero } from '@/components/Hero'
import CareerPathsGrid from '@/components/sections/CareerPathsGrid'
import SkillAIBridgeBand from '@/components/sections/SkillAIBridgeBand'
import Pricing from '@/components/sections/Pricing'
import FAQ from '@/components/sections/FAQ'

export default function HomePage() {
  return (
    <Layout>
      <Head>
        <title>SkillForge Global – Forge your path to success</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <Hero />
      <CareerPathsGrid />
      <SkillAIBridgeBand />
      <Pricing />
      <FAQ />
    </Layout>
  )
}
