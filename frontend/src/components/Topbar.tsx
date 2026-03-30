"use client"
import { useState, useRef, useEffect } from 'react'
import { Bell, Search, UserCircle, LogOut, Settings, Key, Zap, AlertTriangle } from 'lucide-react'

export default function Topbar() {
    const [isProfileOpen, setIsProfileOpen] = useState(false)
    const [isNotifOpen, setIsNotifOpen] = useState(false)

    const profileRef = useRef<HTMLDivElement>(null)
    const notifRef = useRef<HTMLDivElement>(null)

    // Handle click outside to close dropdowns
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
                setIsProfileOpen(false)
            }
            if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
                setIsNotifOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    return (
        <header className="h-16 glass-panel border-b border-gray-800 flex items-center justify-between px-6 z-50 relative">
            <div className="flex items-center bg-secondary/50 rounded-lg px-4 py-2 border border-gray-700/50 w-80 focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
                <Search className="w-4 h-4 text-gray-400 mr-2" />
                <input
                    type="text"
                    placeholder="Search models, active datasets..."
                    className="bg-transparent border-none outline-none text-sm text-white w-full placeholder-gray-500"
                />
            </div>

            <div className="flex items-center space-x-5 relative">
                {/* Notifications */}
                <div className="relative" ref={notifRef}>
                    <button
                        onClick={() => {
                            setIsNotifOpen(!isNotifOpen)
                            setIsProfileOpen(false)
                        }}
                        className="p-2 text-gray-400 hover:text-white transition-colors relative group"
                    >
                        <Bell className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                        <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-accent rounded-full border-2 border-[#0f172a]"></span>
                    </button>

                    {isNotifOpen && (
                        <div className="absolute right-0 mt-2 w-80 glass-panel rounded-xl shadow-2xl border border-white/5 overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200 z-50">
                            <div className="p-4 border-b border-white/5 bg-slate-900/50">
                                <h3 className="text-sm font-bold text-white flex items-center justify-between">
                                    Notifications <span className="bg-primary/20 text-primary text-[10px] px-2 py-0.5 rounded-full">2 New</span>
                                </h3>
                            </div>
                            <div className="max-h-80 overflow-y-auto">
                                <button className="w-full text-left p-4 hover:bg-white/5 border-b border-white/5 transition-colors flex items-start space-x-3">
                                    <div className="bg-emerald-500/20 p-2 rounded-full mt-1">
                                        <Zap className="w-4 h-4 text-emerald-500" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-white font-medium">Model Training Complete</p>
                                        <p className="text-xs text-gray-400 mt-1">LSTM models for Brent Crude (BZ=F) have finished retraining with new RMSE metrics.</p>
                                        <p className="text-[10px] text-gray-500 mt-2">12 mins ago</p>
                                    </div>
                                </button>
                                <button className="w-full text-left p-4 hover:bg-white/5 transition-colors flex items-start space-x-3">
                                    <div className="bg-rose-500/20 p-2 rounded-full mt-1">
                                        <AlertTriangle className="w-4 h-4 text-rose-500" />
                                    </div>
                                    <div>
                                        <p className="text-sm text-white font-medium">High Volatility Detected</p>
                                        <p className="text-xs text-gray-400 mt-1">WTI Crude Oil (CL=F) experiencing unusual price swings &gt; 2.5% in the last hour.</p>
                                        <p className="text-[10px] text-gray-500 mt-2">1 hour ago</p>
                                    </div>
                                </button>
                            </div>
                            <div className="p-2 bg-slate-900/50 border-t border-white/5 text-center">
                                <button className="text-xs text-primary hover:text-primary/80 font-bold transition-colors p-2">Mark all as read</button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="h-8 w-px bg-gray-700"></div>

                {/* Profile */}
                <div className="relative" ref={profileRef}>
                    <button
                        onClick={() => {
                            setIsProfileOpen(!isProfileOpen)
                            setIsNotifOpen(false)
                        }}
                        className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors group"
                    >
                        <div className="bg-primary/20 p-1 rounded-full group-hover:bg-primary/30 transition-colors">
                            <UserCircle className="w-6 h-6 text-primary" />
                        </div>
                        <span className="text-sm font-medium tracking-wide">Quant Analyst</span>
                    </button>

                    {isProfileOpen && (
                        <div className="absolute right-0 mt-3 w-56 glass-panel rounded-xl shadow-2xl border border-white/5 overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200 z-50">
                            <div className="px-4 pt-4 pb-3 border-b border-white/5 bg-slate-900/50">
                                <p className="text-sm font-bold text-white">Quant Analyst</p>
                                <p className="text-xs text-gray-400 mt-0.5">admin@oilcast.ai</p>
                            </div>
                            <div className="py-2">
                                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors flex items-center">
                                    <Settings className="w-4 h-4 mr-3 text-gray-400" /> Account Settings
                                </button>
                                <button className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5 transition-colors flex items-center">
                                    <Key className="w-4 h-4 mr-3 text-gray-400" /> API Keys
                                </button>
                            </div>
                            <div className="py-2 border-t border-white/5 bg-slate-900/30">
                                <button className="w-full text-left px-4 py-2 text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors flex items-center">
                                    <LogOut className="w-4 h-4 mr-3" /> Sign Out
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    )
}
