"use client"
import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function LayoutWrapper({
    children,
    interClassName
}: {
    children: React.ReactNode
    interClassName: string
}) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)
    const pathname = usePathname()

    // Close sidebar when navigating on mobile
    useEffect(() => {
        setIsSidebarOpen(false)
    }, [pathname])

    return (
        <body className={`${interClassName} flex h-screen overflow-hidden`}>
            {/* Backdrop for mobile */}
            {isSidebarOpen && (
                <div 
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden transition-opacity duration-300"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}
            
            <Sidebar isOpen={isSidebarOpen} />
            
            <div className="flex-1 flex flex-col overflow-hidden">
                <Topbar onMenuClick={() => setIsSidebarOpen(true)} />
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[#0f172a] p-4 md:p-6 text-foreground relative">
                    {/* Background ambient glow effect */}
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] pointer-events-none -z-10"></div>
                    <div className="absolute bottom-1/4 right-0 w-80 h-80 bg-accent/10 rounded-full blur-[100px] pointer-events-none -z-10"></div>
                    {children}
                </main>
            </div>
        </body>
    )
}
