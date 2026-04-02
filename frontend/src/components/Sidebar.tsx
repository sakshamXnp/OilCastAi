"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, LineChart, Database, Settings, Droplet, BarChart3 } from 'lucide-react'

const navItems = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Oil Prices', href: '/oil-prices', icon: BarChart3 },
    { name: 'Predictions', href: '/predict', icon: LineChart },
    { name: 'Data Explorer', href: '/explore', icon: Database },
    { name: 'Admin Tools', href: '/admin', icon: Settings },
]

export default function Sidebar({ isOpen }: { isOpen: boolean }) {
    const pathname = usePathname()

    return (
        <aside className={`fixed lg:static inset-y-0 left-0 w-64 glass-panel border-r border-gray-800 flex flex-col transition-all duration-300 z-40 transform ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
            <div className="h-16 flex items-center px-6 border-b border-gray-800">
                <Droplet className="w-6 h-6 text-primary mr-2 shadow-primary/50" />
                <span className="text-xl font-bold tracking-tight text-white shadow-sm">OilCast AI</span>
            </div>
            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 group ${isActive
                                    ? 'bg-primary/20 text-primary border border-primary/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 mr-3 ${isActive ? 'text-primary' : 'text-gray-400 group-hover:text-white transition-colors'}`} />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    )
                })}
            </nav>
            <div className="p-4 border-t border-gray-800 bg-secondary/30">
                <div className="text-xs text-gray-400 text-center font-mono">
                    MVP v1.0.0
                </div>
            </div>
        </aside>
    )
}
