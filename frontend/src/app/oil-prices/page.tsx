"use client"
import { useEffect, useState } from 'react'
import {
    TrendingUp, TrendingDown, Clock, Globe, BarChart3,
    Fuel, Flag, MapPin, Droplet, RefreshCw, Minus
} from 'lucide-react'
import { getOilPrices, OilPriceEntry, OilPricesGrouped } from '@/lib/api'

interface CategoryConfig {
    key: keyof OilPricesGrouped
    label: string
    icon: any
    description: string
    accent: string
    accentBg: string
}

const CATEGORIES: CategoryConfig[] = [
    {
        key: 'futures_indexes',
        label: 'Futures & Indexes',
        icon: BarChart3,
        description: 'Major global crude oil futures and benchmark indexes',
        accent: 'text-blue-400',
        accentBg: 'bg-blue-500/10 border-blue-500/20',
    },
    {
        key: 'opec_members',
        label: 'OPEC Members',
        icon: Globe,
        description: 'Official OPEC member crude oil reference prices',
        accent: 'text-emerald-400',
        accentBg: 'bg-emerald-500/10 border-emerald-500/20',
    },
    {
        key: 'international',
        label: 'International Prices',
        icon: Flag,
        description: 'International crude blends from producing nations worldwide',
        accent: 'text-amber-400',
        accentBg: 'bg-amber-500/10 border-amber-500/20',
    },
    {
        key: 'canadian_blends',
        label: 'Canadian Blends',
        icon: MapPin,
        description: 'Western Canadian crude oil blends and synthetic grades',
        accent: 'text-rose-400',
        accentBg: 'bg-rose-500/10 border-rose-500/20',
    },
    {
        key: 'us_blends',
        label: 'United States Blends',
        icon: Fuel,
        description: 'Domestic US crude oil blends by state and region',
        accent: 'text-violet-400',
        accentBg: 'bg-violet-500/10 border-violet-500/20',
    },
]

function PriceRow({ entry, index }: { entry: OilPriceEntry; index: number }) {
    const isPositive = entry.change >= 0
    const changeColor = entry.change === 0
        ? 'text-gray-500'
        : isPositive ? 'text-emerald-400' : 'text-rose-400'
    const changeBg = entry.change === 0
        ? 'bg-gray-500/5'
        : isPositive ? 'bg-emerald-500/5' : 'bg-rose-500/5'

    return (
        <tr
            className={`group border-b border-white/[0.03] hover:bg-white/[0.03] transition-all duration-200 ${index % 2 === 0 ? 'bg-white/[0.01]' : ''
                }`}
            style={{ animationDelay: `${index * 30}ms` }}
        >
            {/* Name */}
            <td className="py-3.5 px-5">
                <div className="flex items-center space-x-3">
                    <div className="flex flex-col">
                        <span className="text-sm font-bold text-white group-hover:text-blue-300 transition-colors">
                            {entry.name}
                        </span>
                        <span className="text-[10px] text-gray-600 font-mono tracking-wider mt-0.5">
                            {entry.symbol}
                        </span>
                    </div>
                </div>
            </td>

            {/* Region */}
            <td className="py-3.5 px-5 hidden md:table-cell">
                <span className="text-xs text-gray-500 font-medium">
                    {entry.region || '—'}
                </span>
            </td>

            {/* Price */}
            <td className="py-3.5 px-5 text-right">
                {entry.has_data ? (
                    <span className="text-sm font-bold text-white tabular-nums font-mono">
                        ${entry.price.toFixed(2)}
                    </span>
                ) : (
                    <span className="text-xs text-gray-600 italic">
                        Pending
                    </span>
                )}
            </td>

            {/* Change $ */}
            <td className="py-3.5 px-5 text-right hidden lg:table-cell">
                {entry.has_data ? (
                    <span className={`text-sm font-bold tabular-nums font-mono ${changeColor}`}>
                        {entry.change > 0 ? '+' : ''}{entry.change.toFixed(2)}
                    </span>
                ) : (
                    <span className="text-xs text-gray-600">—</span>
                )}
            </td>

            {/* Change % */}
            <td className="py-3.5 px-5 text-right">
                {entry.has_data ? (
                    <div className="flex items-center justify-end space-x-1.5">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-black tabular-nums ${changeBg} ${changeColor}`}>
                            {entry.change_pct > 0 ? (
                                <TrendingUp className="w-3 h-3 mr-1" />
                            ) : entry.change_pct < 0 ? (
                                <TrendingDown className="w-3 h-3 mr-1" />
                            ) : (
                                <Minus className="w-3 h-3 mr-1" />
                            )}
                            {entry.change_pct > 0 ? '+' : ''}{entry.change_pct.toFixed(2)}%
                        </span>
                    </div>
                ) : (
                    <span className="text-xs text-gray-600">—</span>
                )}
            </td>
        </tr>
    )
}

function CategoryTable({ category, data }: { category: CategoryConfig; data: OilPriceEntry[] }) {
    const Icon = category.icon
    // Group by region within international and us_blends
    const shouldGroupByRegion = category.key === 'international' || category.key === 'us_blends'

    let regionGroups: Record<string, OilPriceEntry[]> = {}
    if (shouldGroupByRegion) {
        data.forEach(entry => {
            const region = entry.region || 'Other'
            if (!regionGroups[region]) regionGroups[region] = []
            regionGroups[region].push(entry)
        })
    }

    return (
        <div className="glass-panel rounded-2xl overflow-hidden border border-white/5 shadow-2xl" id={`section-${category.key}`}>
            {/* Category Header */}
            <div className={`p-6 border-b border-white/5 flex items-center justify-between ${category.accentBg}`}>
                <div className="flex items-center space-x-4">
                    <div className={`p-2.5 rounded-xl ${category.accentBg}`}>
                        <Icon className={`w-5 h-5 ${category.accent}`} />
                    </div>
                    <div>
                        <h2 className={`text-lg font-black tracking-tight ${category.accent}`}>
                            {category.label}
                        </h2>
                        <p className="text-[11px] text-gray-500 font-medium mt-0.5">
                            {category.description}
                        </p>
                    </div>
                </div>
                <div className="text-[10px] font-black text-gray-600 px-3 py-1.5 rounded-lg bg-slate-900/50 border border-white/5 tracking-widest">
                    {data.length} BENCHMARKS
                </div>
            </div>

            {/* Price Table */}
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/5 bg-slate-900/30">
                            <th className="py-3 px-5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Crude Oil</th>
                            <th className="py-3 px-5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest hidden md:table-cell">Region</th>
                            <th className="py-3 px-5 text-right text-[10px] font-black text-gray-500 uppercase tracking-widest">Price (USD)</th>
                            <th className="py-3 px-5 text-right text-[10px] font-black text-gray-500 uppercase tracking-widest hidden lg:table-cell">Change</th>
                            <th className="py-3 px-5 text-right text-[10px] font-black text-gray-500 uppercase tracking-widest">% Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        {shouldGroupByRegion ? (
                            Object.entries(regionGroups).map(([region, entries]) => (
                                <>
                                    <tr key={`header-${region}`} className="bg-white/[0.02]">
                                        <td colSpan={5} className="py-2 px-5">
                                            <span className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] flex items-center">
                                                <MapPin className="w-3 h-3 mr-2 opacity-50" />
                                                {region}
                                            </span>
                                        </td>
                                    </tr>
                                    {entries.map((entry, idx) => (
                                        <PriceRow key={entry.symbol} entry={entry} index={idx} />
                                    ))}
                                </>
                            ))
                        ) : (
                            data.map((entry, idx) => (
                                <PriceRow key={entry.symbol} entry={entry} index={idx} />
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default function OilPricesPage() {
    const [data, setData] = useState<OilPricesGrouped | null>(null)
    const [loading, setLoading] = useState(true)
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
    const [activeTab, setActiveTab] = useState<string>('all')

    const fetchData = async () => {
        setLoading(true)
        try {
            const result = await getOilPrices()
            setData(result)
            setLastUpdated(new Date())
        } catch (e) {
            console.error('Failed to fetch oil prices:', e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
        // Auto-refresh every 5 minutes
        const interval = setInterval(fetchData, 300000)
        return () => clearInterval(interval)
    }, [])

    const totalBenchmarks = data
        ? Object.values(data).reduce((sum, arr) => sum + arr.length, 0)
        : 0

    const activeBenchmarks = data
        ? Object.values(data).flat().filter(e => e.has_data).length
        : 0

    const filteredCategories = activeTab === 'all'
        ? CATEGORIES
        : CATEGORIES.filter(c => c.key === activeTab)

    return (
        <div className="min-h-screen pb-12 space-y-8 animate-in fade-in duration-500">
            {/* Page Header */}
            <div className="px-6 pt-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tighter flex items-center">
                            <Droplet className="w-6 h-6 sm:w-9 sm:h-9 mr-3 text-blue-400" />
                            OIL PRICE CHARTS
                            <span className="ml-3 px-2 py-0.5 bg-blue-500/20 text-blue-400 text-[9px] sm:text-[10px] rounded-lg uppercase tracking-widest font-black border border-blue-500/20">
                                Live
                            </span>
                        </h1>
                        <p className="text-gray-500 mt-2 flex items-center text-sm font-medium" suppressHydrationWarning>
                            <Clock className="w-3.5 h-3.5 mr-2 text-blue-400" />
                            {totalBenchmarks} Global Crude Blends & Indexes •
                            {lastUpdated ? ` Updated ${lastUpdated.toLocaleTimeString()}` : ' Loading...'}
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:flex items-center gap-4">
                        {/* Stats Cards */}
                        <div className="glass-panel px-5 py-3 rounded-xl border-l-4 border-l-blue-500">
                            <p className="text-[10px] uppercase tracking-widest font-black text-gray-600">Benchmarks</p>
                            <p className="text-lg sm:text-xl font-black text-white mt-0.5">{totalBenchmarks}</p>
                        </div>
                        <div className="glass-panel px-5 py-3 rounded-xl border-l-4 border-l-emerald-500">
                            <p className="text-[10px] uppercase tracking-widest font-black text-gray-600">Live Data</p>
                            <p className="text-lg sm:text-xl font-black text-emerald-400 mt-0.5">{activeBenchmarks}</p>
                        </div>

                        <button
                            onClick={fetchData}
                            disabled={loading}
                            className="glass-panel p-3 rounded-xl hover:bg-white/10 transition-all border border-white/5 disabled:opacity-50 w-full sm:w-auto flex justify-center"
                        >
                            <RefreshCw className={`w-5 h-5 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Category Tab Navigation */}
            <div className="px-6">
                <div className="flex flex-wrap items-center gap-2 p-1.5 glass-panel rounded-2xl border border-white/5 w-fit">
                    <button
                        onClick={() => setActiveTab('all')}
                        className={`px-5 py-2.5 rounded-xl text-xs font-black tracking-widest transition-all ${activeTab === 'all'
                                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/20 shadow-lg'
                                : 'text-gray-500 hover:text-gray-300 border border-transparent'
                            }`}
                    >
                        ALL PRICES
                    </button>
                    {CATEGORIES.map(cat => (
                        <button
                            key={cat.key}
                            onClick={() => setActiveTab(cat.key)}
                            className={`px-4 py-2.5 rounded-xl text-xs font-black tracking-widest transition-all ${activeTab === cat.key
                                    ? `${cat.accentBg} ${cat.accent} shadow-lg`
                                    : 'text-gray-500 hover:text-gray-300 border border-transparent'
                                }`}
                        >
                            {cat.label.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Loading State */}
            {loading && !data && (
                <div className="px-6">
                    <div className="glass-panel rounded-2xl p-20 flex flex-col items-center justify-center">
                        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-6" />
                        <p className="text-gray-500 text-xs font-black tracking-widest uppercase">
                            Loading Global Oil Market Data...
                        </p>
                    </div>
                </div>
            )}

            {/* Category Tables */}
            {data && (
                <div className="px-6 space-y-8">
                    {filteredCategories.map(category => {
                        const categoryData = data[category.key]
                        if (!categoryData || categoryData.length === 0) return null
                        return (
                            <CategoryTable
                                key={category.key}
                                category={category}
                                data={categoryData}
                            />
                        )
                    })}
                </div>
            )}

            {/* Footer Note */}
            <div className="px-6">
                <div className="glass-panel rounded-xl p-4 border border-white/5">
                    <p className="text-[10px] text-gray-600 text-center font-medium tracking-wide">
                        Price data sourced from Yahoo Finance for major benchmarks. Regional and OPEC blends show reference pricing when available.
                        Data refreshes automatically every 5 minutes. All prices in USD per barrel.
                    </p>
                </div>
            </div>
        </div>
    )
}
