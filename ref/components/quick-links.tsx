import { Route, Compass, CloudSun, Footprints } from "lucide-react"

const links = [
  {
    icon: Route,
    title: "Wari Route",
    desc: "Follow the palkhi path to Pandharpur",
  },
  {
    icon: Compass,
    title: "Near Me",
    desc: "Seva camps, water & rest stops",
  },
  {
    icon: CloudSun,
    title: "Weather",
    desc: "Monsoon updates along the march",
  },
  {
    icon: Footprints,
    title: "My Journey",
    desc: "Track distance walked & darshan",
  },
]

export function QuickLinks() {
  return (
    <section className="px-6 pb-8" aria-labelledby="quick-links-heading">
      <h2
        id="quick-links-heading"
        className="mb-4 font-serif text-xl text-accent"
      >
        Continue your Wari
      </h2>
      <div className="grid grid-cols-2 gap-3">
        {links.map(({ icon: Icon, title, desc }) => (
          <button
            key={title}
            type="button"
            className="flex flex-col items-start gap-2 rounded-2xl border border-border bg-card p-4 text-left transition-all duration-200 hover:border-primary/50 hover:shadow-md active:scale-[0.98]"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-accent">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="font-sans text-sm font-semibold text-foreground">{title}</span>
            <span className="text-xs leading-snug text-muted-foreground">{desc}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
