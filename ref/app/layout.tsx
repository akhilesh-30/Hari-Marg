import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Marcellus, Mukta } from 'next/font/google'
import './globals.css'

const heading = Marcellus({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-heading',
})

const body = Mukta({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-body',
})

export const metadata: Metadata = {
  title: 'Hari Marg — Your Digital Wari Companion',
  description:
    'Hari Marg is your digital Wari companion for the pilgrimage to Pandharpur — routes, weather, nearby stops, and darshan of Lord Vitthal.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light',
  themeColor: '#FDF6EC',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`bg-background ${heading.variable} ${body.variable}`}>
      <body className="font-sans antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
