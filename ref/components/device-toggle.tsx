"use client"

import { Monitor, Smartphone } from "lucide-react"

export type DeviceView = "desktop" | "phone"

export function DeviceToggle({
  view,
  onChange,
}: {
  view: DeviceView
  onChange: (view: DeviceView) => void
}) {
  const options: { value: DeviceView; label: string; icon: typeof Monitor }[] = [
    { value: "desktop", label: "Desktop", icon: Monitor },
    { value: "phone", label: "Phone", icon: Smartphone },
  ]

  return (
    <div className="fixed bottom-5 right-5 z-[60]">
      <div
        role="group"
        aria-label="Preview device"
        className="flex items-center gap-1 rounded-full border border-border bg-card/95 p-1.5 shadow-xl shadow-accent/15 backdrop-blur-md"
      >
        {options.map(({ value, label, icon: Icon }) => {
          const isActive = view === value
          return (
            <button
              key={value}
              type="button"
              onClick={() => onChange(value)}
              aria-pressed={isActive}
              className={`inline-flex items-center gap-2 rounded-full px-4 py-2 font-sans text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-md shadow-primary/30"
                  : "text-muted-foreground hover:text-accent"
              }`}
            >
              <Icon className="h-4 w-4" aria-hidden="true" />
              {label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
