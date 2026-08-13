"use client"

import { useState } from "react"
import { DesktopHome } from "@/components/desktop-home"
import { PhonePreview } from "@/components/phone-preview"
import { DeviceToggle, type DeviceView } from "@/components/device-toggle"

export default function Page() {
  const [view, setView] = useState<DeviceView>("desktop")

  return (
    <>
      <div className="hm-fade-in" key={view}>
        {view === "desktop" ? <DesktopHome /> : <PhonePreview />}
      </div>
      <DeviceToggle view={view} onChange={setView} />
    </>
  )
}
