import { Button } from './Button'
import { motion } from 'framer-motion'
import Link from 'next/link'

export function Hero() {
  return (
    <section className="relative bg-hero-gradient bg-neural overflow-hidden">
      <div className="container pt-28 md:pt-32 pb-16 md:pb-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Text */}
          <div className="text-center md:text-left">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl md:text-6xl font-extrabold leading-tight"
            >
              Global tech careers are <span className="gradient-text">now within reach.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.05 }}
              className="mt-5 text-base md:text-lg text-techGray max-w-2xl mx-auto md:mx-0"
            >
              SkillForge Global gives you the skills, the guidance, and the opportunities to succeed in the world of technology.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1 }}
              className="mt-8 flex flex-col sm:flex-row gap-4 justify-center md:justify-start"
            >
              <Link href="/signup"><Button size="lg">Start forging your future</Button></Link>
              <Link href="/ai"><Button variant="secondary" size="lg">Try SkillAIBridge</Button></Link>
            </motion.div>
          </div>

          {/* Visual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7 }}
            className="relative h-[320px] md:h-[440px] flex items-center justify-center"
          >
            <div className="absolute -inset-12 rounded-full blur-3xl opacity-30 bg-gradient-to-r from-forgePurple to-neuralBlue" />
            <svg className="relative w-[340px] md:w-[440px] h-[340px] md:h-[440px]" viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#6B3BFF" />
                  <stop offset="100%" stopColor="#1E9EFF" />
                </linearGradient>
              </defs>
              <circle cx="300" cy="300" r="220" fill="none" stroke="url(#lg)" strokeWidth="3" />
              {Array.from({ length: 24 }).map((_, i) => {
                const angle = (i / 24) * Math.PI * 2
                const x = 300 + Math.cos(angle) * 220
                const y = 300 + Math.sin(angle) * 220
                return <circle key={i} cx={x} cy={y} r="6" fill={i % 2 ? '#1E9EFF' : '#6B3BFF'} />
              })}
              <path d="M300 80 L500 300 L300 520 L100 300 Z" stroke="url(#lg)" strokeWidth="2" fill="none" />
            </svg>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
