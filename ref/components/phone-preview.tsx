import { HeroSection } from "@/components/hero-section"
import { QuickLinks } from "@/components/quick-links"
import { BottomNav } from "@/components/bottom-nav"

export function PhonePreview() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-secondary/40 px-4 py-16">
      <p className="mb-8 text-center font-serif text-2xl text-accent">
        Hari Marg on mobile
        <span className="mt-1 block font-sans text-sm font-normal text-muted-foreground">
          The Wari companion in your pocket
        </span>
      </p>

      {/* Phone frame */}
      <div className="relative h-[780px] w-[380px] rounded-[3rem] border-[12px] border-accent bg-accent p-0 shadow-2xl shadow-accent/30">
        {/* Notch */}
        <div className="absolute left-1/2 top-0 z-50 h-6 w-36 -translate-x-1/2 rounded-b-2xl bg-accent" />

        {/* Screen */}
        <div className="relative h-full w-full overflow-hidden rounded-[2.2rem] bg-background">
          <div className="hm-scroll h-full overflow-y-auto pb-24">
            <header className="flex items-center justify-between px-6 pt-6">
              <div className="flex items-center gap-2">
                <span
                  aria-hidden="true"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-accent font-serif text-sm text-accent-foreground"
                >
                  ॐ
                </span>
                <span className="font-serif text-lg text-accent">Hari Marg</span>
              </div>
              <span className="rounded-full bg-secondary px-3 py-1 font-sans text-xs font-medium text-secondary-foreground">
                Wari 2026
              </span>
            </header>

            <HeroSection />
            <QuickLinks />
          </div>

          <BottomNav variant="contained" />
        </div>
      </div>
    </div>
  )
}
