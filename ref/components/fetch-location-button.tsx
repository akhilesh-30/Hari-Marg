"use client"

import { useState } from "react"
import { MapPin, LoaderCircle, Check } from "lucide-react"

type LocationState = "idle" | "loading" | "success" | "error"

export function FetchLocationButton({ size = "md" }: { size?: "md" | "lg" }) {
  const [state, setState] = useState<LocationState>("idle")
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null)

  function fetchLocation() {
    if (!("geolocation" in navigator)) {
      setState("error")
      return
    }
    setState("loading")
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setState("success")
      },
      () => setState("error"),
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  const sizeClasses =
    size === "lg" ? "px-9 py-4 text-lg gap-3" : "px-8 py-3.5 text-base gap-2.5"
  const iconSize = size === "lg" ? "h-5 w-5" : "h-5 w-5"

  return (
    <div>
      <button
        type="button"
        onClick={fetchLocation}
        disabled={state === "loading"}
        className={`group relative inline-flex items-center rounded-full bg-primary font-sans font-semibold text-primary-foreground shadow-lg shadow-primary/30 transition-all duration-200 hover:brightness-105 active:scale-95 disabled:opacity-80 ${sizeClasses}`}
      >
        <span aria-hidden="true" className="absolute inset-0 -z-10 rounded-full">
          {state === "idle" && (
            <span className="hm-ping-slow absolute inset-0 rounded-full bg-primary/40" />
          )}
        </span>
        {state === "loading" ? (
          <LoaderCircle className={`${iconSize} animate-spin`} aria-hidden="true" />
        ) : state === "success" ? (
          <Check className={iconSize} aria-hidden="true" />
        ) : (
          <MapPin className={iconSize} aria-hidden="true" />
        )}
        {state === "loading"
          ? "Finding you..."
          : state === "success"
            ? "Location Found"
            : "Fetch My Location"}
      </button>

      <div className="mt-3 min-h-5 text-sm" aria-live="polite">
        {state === "success" && coords && (
          <p className="text-secondary-foreground">
            {`On the path at ${coords.lat.toFixed(3)}°, ${coords.lng.toFixed(3)}°`}
          </p>
        )}
        {state === "error" && (
          <p className="text-primary">Couldn&apos;t access location. Please enable it and try again.</p>
        )}
      </div>
    </div>
  )
}
