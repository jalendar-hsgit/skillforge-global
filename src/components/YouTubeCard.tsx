export function YouTubeCard({ title, youtubeId, duration }: { title:string; youtubeId:string; duration?:string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.06] overflow-hidden">
      <div className="aspect-video">
        <iframe
          className="w-full h-full"
          src={`https://www.youtube.com/embed/${youtubeId}`}
          title={title}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerPolicy="strict-origin-when-cross-origin"
          allowFullScreen
        />
      </div>
      <div className="p-4">
        <div className="text-sm font-semibold">{title}</div>
        {duration && <div className="text-xs text-techGray mt-1">{duration}</div>}
      </div>
    </div>
  )
}
