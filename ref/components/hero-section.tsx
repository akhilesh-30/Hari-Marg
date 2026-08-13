import Image from "next/image"
import { FetchLocationButton } from "@/components/fetch-location-button"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden px-6 pb-10 pt-8 text-center">
      {/* Devotional image with animated glow halo */}
      <div className="relative mx-auto mb-6 flex h-56 w-56 items-center justify-center">
        <div
          aria-hidden="true"
          className="hm-glow absolute inset-0 rounded-full bg-primary/25 blur-2xl"
        />
        <div className="hm-float relative h-52 w-52 overflow-hidden rounded-full border-4 border-accent/70 shadow-xl shadow-accent/20">
          <Image
            src="/images/vitthal.png"
            alt="Illustration of Lord Vitthal, the presiding deity of the Pandharpur Wari pilgrimage"
            fill
            priority
            sizes="208px"
            className="object-cover"
          />
        </div>
      </div>

      <p
        className="hm-fade-up mb-3 font-sans text-xs font-semibold uppercase tracking-[0.25em] text-accent"
        style={{ animationDelay: "0.05s" }}
      >
        {"॥ विठ्ठल विठ्ठल ॥"}
      </p>

      <h1
        className="hm-fade-up text-balance font-serif text-4xl leading-tight text-accent"
        style={{ animationDelay: "0.15s" }}
      >
        Hari Marg
        <span className="mt-1 block text-2xl text-primary">Your Digital Wari Companion</span>
      </h1>

      <p
        className="hm-fade-up mx-auto mt-4 max-w-sm text-pretty text-base leading-relaxed text-muted-foreground"
        style={{ animationDelay: "0.25s" }}
      >
        Walk the sacred road to Pandharpur with confidence — live routes, nearby seva stops,
        and weather along the way, all in one companion.
      </p>

      <div className="hm-fade-up mt-8 flex justify-center" style={{ animationDelay: "0.35s" }}>
        <FetchLocationButton />
      </div>
    </section>
  )
}
