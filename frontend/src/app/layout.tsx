import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'OilCast AI',
    description: 'AI-powered MVP that predicts global crude oil prices',
}

import LayoutWrapper from '@/components/LayoutWrapper'

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <LayoutWrapper interClassName={inter.className}>
                {children}
            </LayoutWrapper>
        </html>
    )
}
