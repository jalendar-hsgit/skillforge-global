import { ReactNode } from 'react'

export function InfoCard({
  title,
  subtitle,
  icon,
  href,
}: {
  title: string
  subtitle: string
  icon: ReactNode
  href?: string
}) {
  const Wrapper = ({ children }: { children: ReactNode }) =>
    href ? <a href={href} className="block">{children}</a> : <div>{children}</div>

  return (
    <Wrapper>
      <div className="rounded-2xl border border-white/10 bg-white/[0.06] hover:bg-white/[0.08] transition backdrop-blur p-5 h-full">
        <div className="flex items-start gap-4">
          <div className="shrink-0 h-12 w-12 rounded-xl bg-gradient-to-br from-forgePurple/40 to-neuralBlue/40 grid place-items-center">
            {icon}
          </div>
          <div>
            <h3 className="text-base font-semibold">{title}</h3>
            <p className="text-sm text-techGray mt-1">{subtitle}</p>
          </div>
        </div>
      </div>
    </Wrapper>
  )
}
