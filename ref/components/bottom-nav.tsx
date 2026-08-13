"use client"

import { useState } from "react"
import { Home, Route, Compass, CloudSun, User, type LucideIcon } from "lucide-react"

type NavItem = {
  label: string
  icon: LucideIcon
}

const items: NavItem[] = [
  { label: "Home", icon: Home },
  { label: "Route", icon: Route },
  { label: "Near Me", icon: Compass },
  { label: "Weather", icon: CloudSun },
  { label: "Profile", icon: User },
]

export function BottomNav({ variant = "fixed" }: { variant?: "fixed" | "contained" }) {
  const [active, setActive] = useState("Home")

  const positionClasses =
    variant === "contained"
      ? "absolute inset-x-0 bottom-0"
      : "fixed inset-x-0 bottom-0 mx-auto max-w-md"

  return (
    <nav
      aria-label="Primary"
      className={`z-50 border-t border-border bg-card/95 backdrop-blur-sm ${positionClasses}`}
    >
      <ul className="flex items-stretch justify-between px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2">
        {items.map(({ label, icon: Icon }) => {
          const isActive = active === label
          return (
            <li key={label} className="flex-1">
              <button
                type="button"
                onClick={() => setActive(label)}
                aria-current={isActive ? "page" : undefined}
                className="flex w-full flex-col items-center gap-1 rounded-xl py-1.5 transition-colors"
              >
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-full transition-all duration-200 ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-md shadow-primary/30"
                      : "text-muted-foreground"
                  }`}
                >
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span
                  className={`font-sans text-[11px] font-medium leading-none ${
                    isActive ? "text-accent" : "text-muted-foreground"
                  }`}
                >
                  {label}
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
