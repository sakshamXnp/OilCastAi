"use client"
import { useEffect, useState } from 'react'
import { getHistory, getCommodities, PriceData, Commodity } from '@/lib/api'
import { Download, Filter, DatabaseZap, ChevronRight } from 'lucide-react'

export default function Explore() {
    const [history, setHistory] = useState<PriceData[]>([])
    const [commodities, setCommodities] = useState<Commodity[]>([])
    const [selectedSymbol, setSelectedSymbol] = useState<string>('WTI')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadComms() {
            try {
                const comms = await getCommodities().catch(() => [])
                setCommodities(comms)
            } catch (e) {
                console.error("Failed to load commodities", e)
            }
        }
        loadComms()
    }, [])

    useEffect(() => {
        async function loadData() {
            setLoading(true)
            try {
                const hist = await getHistory(selectedSymbol, 1000).catch(() => [])
                setHistory([...hist].reverse()) // newest first
            } catch (e) {
                console.error("Error loading history:", e)
            } finally {
                setLoading(false)
            }
        }
        loadData()
    }, [selectedSymbol])

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-white mb-2 flex items-center">
                        <DatabaseZap className="w-8 h-8 mr-3 text-primary animate-pulse" />
                        DATA EXPLORER
                    </h1>
                    <p className="text-gray-400 text-sm font-medium uppercase tracking-widest opacity-60">Global Commodity Historical Repository</p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <select
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                        className="bg-slate-900 border border-white/10 text-white text-sm rounded-xl px-6 py-2.5 outline-none focus:ring-2 focus:ring-primary/50 transition-all cursor-pointer font-bold tracking-wider"
                    >
                        {commodities.map(c => (
                            <option key={c.symbol} value={c.symbol}>{c.symbol} - {c.name}</option>
                        ))}
                        {commodities.length === 0 && (
                            <>
                                <option value="WTI">WTI Crude Oil</option>
                                <option value="BRENT">Brent Crude Oil</option>
                            </>
                        )}
                    </select>

                    <button className="flex items-center px-6 py-2.5 glass-panel hover:bg-white/10 rounded-xl text-sm font-bold transition-all border border-white/5 uppercase tracking-widest text-gray-400">
                        <Filter className="w-4 h-4 mr-2" />
                        Sort
                    </button>
                    <button className="flex items-center px-6 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-xl text-sm font-black transition-all shadow-[0_4px_20px_rgba(59,130,246,0.3)] uppercase tracking-widest">
                        <Download className="w-4 h-4 mr-2" />
                        Export CSV
                    </button>
                </div>
            </div>

            <div className="glass-panel rounded-3xl overflow-hidden flex flex-col h-[700px] border border-white/5 shadow-2xl">
                <div className="p-6 border-b border-white/5 flex justify-between items-center bg-slate-900/40">
                    <div className="flex items-center space-x-4">
                        <div className="bg-primary/20 p-2 rounded-lg">
                            <Activity className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-black text-white tracking-widest uppercase text-sm">
                                {selectedSymbol} Historical Time-Series
                            </h3>
                            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-tight">Verified Market Data Points</p>
                        </div>
                    </div>
                    <div className="text-xs font-black text-primary px-4 py-2 rounded-xl bg-primary/10 border border-primary/20 tracking-widest">
                        {history.length} RECORDS FOUND
                    </div>
                </div>

                <div className="flex-1 overflow-auto custom-scrollbar">
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-[#0f172a] z-10 shadow-xl">
                            <tr className="border-b border-white/5">
                                <th className="p-6 text-[10px] tracking-widest text-gray-500 font-black uppercase w-1/3">Transaction Timestamp</th>
                                <th className="p-6 text-[10px] tracking-widest text-gray-500 font-black uppercase w-1/3 text-center">Benchmark</th>
                                <th className="p-6 text-[10px] tracking-widest text-gray-500 font-black uppercase text-right w-1/3">Closing Value (USD)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan={3} className="p-20 text-center">
                                        <div className="flex flex-col items-center">
                                            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
                                            <span className="text-gray-500 font-black text-xs tracking-widest uppercase">Fetching Encrypted Ledger...</span>
                                        </div>
                                    </td>
                                </tr>
                            ) : history.length > 0 ? (
                                history.map(row => (
                                    <tr key={row.id} className="hover:bg-primary/5 transition-all group">
                                        <td className="p-6 text-sm text-gray-300 font-bold group-hover:text-white transition-colors">
                                            {new Date(row.timestamp).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                                        </td>
                                        <td className="p-6 text-sm text-center">
                                            <span className="px-3 py-1.5 bg-slate-900 rounded-lg text-[10px] font-black border border-white/5 shadow-inner text-gray-400 group-hover:text-primary group-hover:border-primary/30 transition-all tracking-widest">
                                                {selectedSymbol}
                                            </span>
                                        </td>
                                        <td className="p-6 text-sm text-white font-black text-right group-hover:text-emerald-400 transition-colors tabular-nums">
                                            ${row.price.toFixed(2)}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={3} className="p-20 text-center flex flex-col items-center">
                                        <AlertCircle className="w-12 h-12 text-gray-700 mb-4" />
                                        <p className="text-gray-500 font-black text-xs tracking-widest uppercase">No verified data in vault.</p>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

import { Activity, AlertCircle } from 'lucide-react'
