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

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={`${inter.className} flex h-screen overflow-hidden`}>
                <Sidebar />
                <div className="flex-1 flex flex-col overflow-hidden">
                    <Topbar />
                    <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[#0f172a] p-6 text-foreground relative">
                        {/* Background ambient glow effect */}
                        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] pointer-events-none -z-10"></div>
                        <div className="absolute bottom-1/4 right-0 w-80 h-80 bg-accent/10 rounded-full blur-[100px] pointer-events-none -z-10"></div>
                        {children}
                    </main>
                </div>
            </body>
        </html>
    )
}
