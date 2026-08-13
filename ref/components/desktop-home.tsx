"use client"

import Image from "next/image"
import { useState } from "react"
import {
  Home,
  Route,
  Compass,
  CloudSun,
  User,
  Footprints,
  MapPin,
  Users,
  Sunrise,
  type LucideIcon,
} from "lucide-react"
import { FetchLocationButton } from "@/components/fetch-location-button"

const navItems = ["Home", "Route", "Near Me", "Weather", "Profile"]

const features: { icon: LucideIcon; title: string; desc: string }[] = [
  { icon: Route, title: "Wari Route", desc: "Follow the live palkhi path from Alandi & Dehu to Pandharpur." },
  { icon: Compass, title: "Near Me", desc: "Find seva camps, water points, and rest stops around you." },
  { icon: CloudSun, title: "Weather", desc: "Monsoon forecasts and heat alerts along the day's march." },
  { icon: Footprints, title: "My Journey", desc: "Track distance walked, dindi group, and darshan slots." },
]

const stats = [
  { value: "250 km", label: "Sacred route" },
  { value: "21 days", label: "Traditional Wari" },
  { value: "9 lakh+", label: "Warkaris walking" },
]

export function DesktopHome() {
  const [active, setActive] = useState("Home")

  return (
    <div className="min-h-screen bg-background">
      {/* Top navigation */}
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-8 py-4">
          <div className="flex items-center gap-2.5">
            <span
              aria-hidden="true"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-accent font-serif text-lg text-accent-foreground"
            >
              ॐ
            </span>
            <span className="font-serif text-2xl text-accent">Hari Marg</span>
          </div>

          <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => {
              const isActive = active === item
              return (
                <button
                  key={item}
                  type="button"
                  onClick={() => setActive(item)}
                  aria-current={isActive ? "page" : undefined}
                  className={`rounded-full px-4 py-2 font-sans text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-secondary text-accent"
                      : "text-muted-foreground hover:text-accent"
                  }`}
                >
                  {item}
                </button>
              )
            })}
          </nav>

          <span className="rounded-full border border-primary/30 bg-secondary px-4 py-1.5 font-sans text-xs font-semibold tracking-wide text-secondary-foreground">
            Wari 2026
          </span>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Decorative rotating rays behind the deity */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute right-[-8rem] top-[-6rem] h-[36rem] w-[36rem] opacity-[0.07]"
          style={{
            background:
              "repeating-conic-gradient(from 0deg, var(--maroon) 0deg 6deg, transparent 6deg 12deg)",
            maskImage: "radial-gradient(circle, black 30%, transparent 68%)",
            WebkitMaskImage: "radial-gradient(circle, black 30%, transparent 68%)",
          }}
        >
          <div className="hm-spin-slow h-full w-full" />
        </div>

        <div className="mx-auto grid max-w-6xl items-center gap-12 px-8 py-20 lg:grid-cols-2">
          {/* Left: copy */}
          <div className="text-center lg:text-left">
            <p
              className="hm-fade-up mb-4 font-sans text-sm font-semibold uppercase tracking-[0.3em] text-accent"
              style={{ animationDelay: "0.05s" }}
            >
              {"॥ विठ्ठल विठ्ठल ॥"}
            </p>
            <h1
              className="hm-fade-up text-balance font-serif text-6xl leading-[1.05] text-accent"
              style={{ animationDelay: "0.15s" }}
            >
              Hari Marg
              <span className="mt-2 block text-4xl text-primary">Your Digital Wari Companion</span>
            </h1>
            <p
              className="hm-fade-up mx-auto mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground lg:mx-0"
              style={{ animationDelay: "0.25s" }}
            >
              Walk the sacred road to Pandharpur with confidence — live palkhi routes, nearby
              seva stops, and weather along the way, all in one devoted companion.
            </p>

            <div
              className="hm-fade-up mt-9 flex flex-col items-center gap-4 sm:flex-row lg:items-start lg:justify-start"
              style={{ animationDelay: "0.35s" }}
            >
              <FetchLocationButton size="lg" />
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-full border border-accent/30 px-7 py-4 font-sans text-lg font-semibold text-accent transition-colors hover:bg-secondary"
              >
                <Route className="h-5 w-5" aria-hidden="true" />
                Explore Route
              </button>
            </div>

            {/* Stats */}
            <dl
              className="hm-fade-up mt-12 grid max-w-lg grid-cols-3 gap-6 border-t border-border pt-8"
              style={{ animationDelay: "0.45s" }}
            >
              {stats.map((s) => (
                <div key={s.label} className="text-center lg:text-left">
                  <dt className="font-serif text-3xl text-primary">{s.value}</dt>
                  <dd className="mt-1 font-sans text-sm text-muted-foreground">{s.label}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Right: deity image with floating chips */}
          <div className="relative mx-auto flex h-[26rem] w-[26rem] max-w-full items-center justify-center">
            <div
              aria-hidden="true"
              className="hm-glow absolute inset-6 rounded-full bg-primary/25 blur-3xl"
            />
            <div className="hm-float relative h-[22rem] w-[22rem] overflow-hidden rounded-full border-[6px] border-accent/70 shadow-2xl shadow-accent/25">
              <Image
                src="/images/vitthal.png"
                alt="Illustration of Lord Vitthal, the presiding deity of the Pandharpur Wari pilgrimage"
                fill
                priority
                sizes="352px"
                className="object-cover"
              />
            </div>

            {/* Floating info chips */}
            <div className="hm-fade-in absolute left-0 top-10 flex items-center gap-2 rounded-2xl border border-border bg-card/95 px-4 py-3 shadow-lg backdrop-blur-sm">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary text-accent">
                <MapPin className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="text-left">
                <p className="font-sans text-xs text-muted-foreground">Next stop</p>
                <p className="font-sans text-sm font-semibold text-foreground">Wakhari · 4 km</p>
              </div>
            </div>

            <div className="hm-fade-in absolute bottom-12 right-0 flex items-center gap-2 rounded-2xl border border-border bg-card/95 px-4 py-3 shadow-lg backdrop-blur-sm">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary text-accent">
                <Sunrise className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="text-left">
                <p className="font-sans text-xs text-muted-foreground">Today</p>
                <p className="font-sans text-sm font-semibold text-foreground">28° · Light rain</p>
              </div>
            </div>

            <div className="hm-fade-in absolute -bottom-2 left-8 flex items-center gap-2 rounded-2xl border border-border bg-card/95 px-4 py-3 shadow-lg backdrop-blur-sm">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary text-accent">
                <Users className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="text-left">
                <p className="font-sans text-xs text-muted-foreground">Your dindi</p>
                <p className="font-sans text-sm font-semibold text-foreground">Sant Tukaram</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-8 pb-24" aria-labelledby="features-heading">
        <div className="mb-10 text-center">
          <h2 id="features-heading" className="font-serif text-4xl text-accent">
            Everything for your Wari
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-pretty text-muted-foreground">
            From the first step in Alandi to darshan at Pandharpur, Hari Marg walks with you.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <button
              key={title}
              type="button"
              className="group flex flex-col items-start gap-4 rounded-3xl border border-border bg-card p-7 text-left transition-all duration-200 hover:-translate-y-1 hover:border-primary/50 hover:shadow-xl hover:shadow-accent/10"
            >
              <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary text-accent transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                <Icon className="h-6 w-6" aria-hidden="true" />
              </span>
              <span className="font-serif text-xl text-accent">{title}</span>
              <span className="text-sm leading-relaxed text-muted-foreground">{desc}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-secondary/40">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-8 py-8 sm:flex-row">
          <div className="flex items-center gap-2.5">
            <span
              aria-hidden="true"
              className="flex h-8 w-8 items-center justify-center rounded-full bg-accent font-serif text-sm text-accent-foreground"
            >
              ॐ
            </span>
            <span className="font-serif text-lg text-accent">Hari Marg</span>
          </div>
          <p className="font-sans text-sm text-muted-foreground">
            Made with devotion for the Warkari sangha · Pandharpur Wari
          </p>
        </div>
      </footer>
    </div>
  )
}
