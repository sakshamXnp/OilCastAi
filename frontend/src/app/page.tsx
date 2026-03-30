"use client"
import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Area, AreaChart, ComposedChart, Cell
} from 'recharts'
import {
    TrendingUp, Activity, DollarSign, AlertCircle,
    Globe, Newspaper, BarChart3, Clock, ChevronRight,
    Search, Filter, Zap, ShieldCheck
} from 'lucide-react'
import {
    getCommodities, getHistory, getPredictions, getMetrics,
    getSentiment, getSentimentScore, getLatestPrices,
    Commodity, PriceData, Prediction, ModelMetric, NewsEvent
} from '@/lib/api'

export default function Dashboard() {
    const [commodities, setCommodities] = useState<Commodity[]>([])
    const [selectedSymbol, setSelectedSymbol] = useState<string>('')
    const [history, setHistory] = useState<PriceData[]>([])
    const [predictions, setPredictions] = useState<Prediction[]>([])
    const [metrics, setMetrics] = useState<ModelMetric[]>([])
    const [sentiment, setSentiment] = useState<NewsEvent[]>([])
    const [sentimentScore, setSentimentScore] = useState<{ score: number; status: string }>({ score: 0, status: 'Neutral' })
    const [latestPrices, setLatestPrices] = useState<any[]>([])

    const [selectedModel, setSelectedModel] = useState<string>('LSTM')
    const [selectedHorizon, setSelectedHorizon] = useState<number>(30)
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')

    // Initial Load: Commodities, Global Sentiment & Latest Prices
    useEffect(() => {
        async function init() {
            try {
                const [comms, sent, score, latest] = await Promise.all([
                    getCommodities().catch(() => []),
                    getSentiment().catch(() => []),
                    getSentimentScore().catch(() => ({ score: 0, status: 'Neutral' })),
                    getLatestPrices().catch(() => [])
                ])
                setCommodities(comms)
                if (comms.length > 0) {
                    // Calibrate to the first commodity in the list (often BZ=F or CL=F)
                    setSelectedSymbol(comms[0].symbol)
                }
                setSentiment(sent)
                setSentimentScore(score)
                setLatestPrices(latest)
            } catch (e) {
                console.error("Initialization failed", e)
            }
        }
        init()

        // Refresh latest prices every 5 minutes
        const interval = setInterval(async () => {
            const latest = await getLatestPrices().catch(() => [])
            setLatestPrices(latest)
        }, 300000)

        return () => clearInterval(interval)
    }, [])

    // Commodity-specific data load
    useEffect(() => {
        if (!selectedSymbol) return

        async function loadCommodityData() {
            setLoading(true)
            try {
                const [hist, preds, m] = await Promise.all([
                    getHistory(selectedSymbol, 60).catch(() => []),
                    getPredictions(selectedSymbol, selectedModel, selectedHorizon).catch(() => []),
                    getMetrics(selectedSymbol).catch(() => [])
                ])
                setHistory(hist)
                setPredictions(preds)
                setMetrics(m)
            } catch (e) {
                console.error(`Error loading data for ${selectedSymbol}`, e)
            } finally {
                setLoading(false)
            }
        }
        loadCommodityData()
    }, [selectedSymbol, selectedModel, selectedHorizon])

    const currentCommodity = commodities.find(c => c.symbol === selectedSymbol)
    const latestPriceData = latestPrices.find(p => p.symbol === selectedSymbol)

    const currentPrice = latestPriceData ? latestPriceData.price : (history.length > 0 ? history[history.length - 1].price : 0)
    const priceChange = history.length > 1 ? ((currentPrice - history[history.length - 2].price) / history[history.length - 2].price) * 100 : 0
    const currentModelMetrics = metrics.find(m => m.model_name === selectedModel)

    // Filtered commodities for the selector
    const filteredCommodities = commodities.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.symbol.toLowerCase().includes(searchTerm.toLowerCase())
    )

    // Chart Data Transformation
    const chartData = useMemo(() => {
        const data: any[] = history.map(h => ({
            date: new Date(h.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            actual: h.price,
            predicted: null,
            lower: null,
            upper: null
        }))

        if (history.length > 0 && predictions.length > 0) {
            const last = history[history.length - 1]
            data.push({
                date: new Date(last.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                actual: null,
                predicted: last.price,
                lower: last.price,
                upper: last.price
            })

            predictions.forEach(p => {
                data.push({
                    date: new Date(p.target_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    actual: null,
                    predicted: parseFloat(p.predicted_price.toFixed(2)),
                    lower: p.confidence_lower ? parseFloat(p.confidence_lower.toFixed(2)) : null,
                    upper: p.confidence_upper ? parseFloat(p.confidence_upper.toFixed(2)) : null
                } as any)
            })
        }
        return data
    }, [history, predictions])

    return (
        <div className="min-h-screen pb-12 space-y-8 animate-in fade-in duration-700">
            {/* 1. Global Intelligence Ticker */}
            <div className="w-full overflow-hidden h-12 glass-panel border-x-0 border-t-0 flex items-center relative z-20">
                <div className="absolute left-0 top-0 bottom-0 px-4 bg-slate-900 flex items-center z-30 font-bold text-primary text-xs tracking-widest border-r border-white/5 uppercase">
                    <Globe className="w-3 h-3 mr-2 animate-pulse" /> Live Benchmarks
                </div>
                <div className="flex animate-ticker whitespace-nowrap pl-40">
                    {(latestPrices.length > 0 ? [...latestPrices, ...latestPrices] : [...commodities, ...commodities]).map((c: any, i) => (
                        <div key={i} className="flex items-center space-x-2 px-8 py-1 border-r border-white/5">
                            <span className="text-gray-400 font-bold text-xs">{c.symbol}</span>
                            <span className="text-white font-mono text-xs">${c.price?.toFixed(2) || '0.00'}</span>
                            <span className={`${(c.change || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'} text-[10px] font-bold`}>
                                {(c.change || 0) >= 0 ? '+' : ''}{(c.change || 0.0).toFixed(1)}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="px-6 space-y-8">
                {/* 2. Header & Quick Metrics */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-black text-white tracking-tighter flex items-center">
                            ENERGY INTELLIGENCE <span className="ml-3 px-2 py-0.5 bg-primary text-[10px] rounded uppercase tracking-widest font-bold">Platform v2.0</span>
                        </h1>
                        <p className="text-gray-400 mt-1 flex items-center text-sm" suppressHydrationWarning>
                            <Clock className="w-3 h-3 mr-2 text-primary" /> Multi-Commodity Global Feed • Updated {latestPriceData ? new Date(latestPriceData.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
                        </p>
                    </div>

                    <div className="grid grid-cols-2 lg:flex items-center gap-4">
                        <div className="glass-panel px-6 py-3 rounded-xl border-l-4 border-l-primary">
                            <p className="text-[10px] uppercase tracking-widest font-bold text-gray-500">Market Sentiment</p>
                            <div className="flex items-center justify-between mt-1">
                                <span className={`text-lg font-bold ${sentimentScore.score > 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                    {sentimentScore.status}
                                </span>
                                <Zap className={`w-4 h-4 ml-4 ${sentimentScore.score > 0 ? 'text-emerald-500' : 'text-amber-500'}`} />
                            </div>
                        </div>
                        <div className="glass-panel px-6 py-3 rounded-xl border-l-4 border-l-emerald-500">
                            <p className="text-[10px] uppercase tracking-widest font-bold text-gray-500">Active Signals</p>
                            <div className="flex items-center justify-between mt-1">
                                <span className="text-lg font-bold text-white">High Reliability</span>
                                <ShieldCheck className="w-4 h-4 ml-4 text-emerald-500" />
                            </div>
                        </div>
                    </div>
                </div>

                    {/* 2b. Global Intelligence - Horizontal Expansion */}
                    <div className="space-y-4 animate-in slide-in-from-top-4 duration-1000">
                        <div className="flex items-center justify-between px-2">
                            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                                <Newspaper className="w-4 h-4 mr-2" /> Global Market News
                            </h3>
                            <Link href="/news">
                                <button className="text-[10px] font-black uppercase tracking-widest text-primary/60 hover:text-primary transition-all flex items-center">
                                    Open Intelligence Feed <ChevronRight className="w-3 h-3 ml-1" />
                                </button>
                            </Link>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {sentiment.length > 0 ? sentiment.slice(0, 3).map((n) => (
                                <div
                                    key={n.id}
                                    className="group relative p-5 rounded-3xl glass-panel hover:border-primary/30 hover:bg-primary/5 transition-all duration-500 cursor-pointer overflow-hidden border-white/5 bg-slate-900/40"
                                    onClick={() => n.url && window.open(n.url, '_blank')}
                                >
                                    <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full -mr-12 -mt-12 blur-2xl group-hover:bg-primary/10 transition-colors" />
                                    
                                    <div className="flex items-center justify-between mb-4 relative z-10">
                                        <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{n.source || 'MARKET INTEL'}</span>
                                        <div className={`w-2 h-2 rounded-full ${n.sentiment_score > 0 ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.6)]' : 'bg-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.6)]'}`} />
                                    </div>

                                    <h4 className="text-sm text-white font-bold leading-relaxed group-hover:text-primary transition-colors line-clamp-3 mb-6 relative z-10">
                                        {n.headline}
                                    </h4>

                                    <div className="flex items-center justify-between mt-auto relative z-10 border-t border-white/5 pt-4">
                                        <span className="text-[10px] text-gray-500 font-bold flex items-center italic">
                                            <Clock className="w-3 h-3 mr-2 opacity-50" />
                                            {new Date(n.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                        </span>
                                        <span className={`text-[9px] font-black tracking-widest uppercase px-2 py-1 rounded bg-white/5 ${n.sentiment_score > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                            {n.sentiment_score > 0 ? 'Bullish' : 'Bearish'}
                                        </span>
                                    </div>
                                </div>
                            )) : (
                                [1, 2, 3].map(i => (
                                    <div key={i} className="h-40 glass-panel rounded-3xl animate-pulse bg-white/5 flex items-center justify-center">
                                        <p className="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Scanning Channel {i}...</p>
                                    </div>
                                ))
                            )}
                        </div>

                        {sentiment.length > 3 && (
                            <div className="flex justify-center mt-4">
                                <Link href="/news">
                                    <button className="px-8 py-3 rounded-2xl bg-primary/10 border border-primary/20 text-primary text-[10px] font-black uppercase tracking-[0.2em] hover:bg-primary hover:text-white transition-all shadow-lg hover:shadow-primary/20 group">
                                        Unlock More Intelligence Signals (+{sentiment.length - 3}) <ChevronRight className="w-4 h-4 ml-2 inline group-hover:translate-x-1 transition-transform" />
                                    </button>
                                </Link>
                            </div>
                        )}
                    </div>


                {/* 3. Main Intelligence Suite */}
                <div className="grid grid-cols-12 gap-8">
                    {/* Left: Commodity Selector */}
                    <div className="col-span-12 lg:col-span-3 space-y-6">
                        <div className="glass-panel p-4 rounded-2xl">
                            <div className="relative mb-4">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Search Commodities..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full bg-slate-900/50 border border-white/5 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary/50 transition-all placeholder:text-gray-600"
                                />
                            </div>

                            <div className="space-y-1 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                                {filteredCommodities.map((c) => (
                                    <button
                                        key={c.symbol}
                                        onClick={() => setSelectedSymbol(c.symbol)}
                                        className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${selectedSymbol === c.symbol ? 'bg-primary/20 border border-primary/30 text-white' : 'hover:bg-white/5 text-gray-400'}`}
                                    >
                                        <div className="text-left">
                                            <div className="font-bold text-xs tracking-wide">{c.symbol}</div>
                                            <div className="text-[10px] opacity-60 truncate max-w-[120px]">{c.name}</div>
                                        </div>
                                        <ChevronRight className={`w-4 h-4 ${selectedSymbol === c.symbol ? 'text-primary' : 'opacity-20'}`} />
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="glass-panel p-6 rounded-2xl glass-panel-blue border-l-4 border-l-primary">
                            <h3 className="text-xs font-bold uppercase tracking-widest text-primary mb-4 flex items-center">
                                <BarChart3 className="w-4 h-4 mr-2" /> Model Performance
                            </h3>
                            {currentModelMetrics ? (
                                <div className="space-y-4">
                                    <div className="flex justify-between items-end">
                                        <span className="text-gray-400 text-xs font-medium">MAPE</span>
                                        <span className="text-white font-bold text-sm">{(currentModelMetrics.mape * 100).toFixed(2)}%</span>
                                    </div>
                                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary"
                                            style={{ width: `${Math.max(10, 100 - currentModelMetrics.mape * 100)}%` }}
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 pt-2">
                                        <div>
                                            <p className="text-[10px] text-gray-500 uppercase font-bold">RMSE</p>
                                            <p className="text-white text-sm font-bold">${currentModelMetrics.rmse.toFixed(2)}</p>
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-gray-500 uppercase font-bold">MAE</p>
                                            <p className="text-white text-sm font-bold">${currentModelMetrics.mae.toFixed(2)}</p>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-gray-500 text-xs italic">Metrics loading...</div>
                            )}
                        </div>
                    </div>

                    {/* Right: Forecast & Charting */}
                    <div className="col-span-12 lg:col-span-9 space-y-8">
                        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
                            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-6">
                                <div>
                                    <div className="flex items-center space-x-3 mb-1">
                                        <span className="text-primary font-black text-2xl uppercase tracking-wider">{selectedSymbol}</span>
                                        <span className="h-6 w-px bg-white/10" />
                                        <span className="text-white text-3xl font-bold tabular-nums">${currentPrice.toFixed(2)}</span>
                                        <span className={`text-sm font-bold ${priceChange >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                            {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
                                        </span>
                                    </div>
                                    <p className="text-gray-500 text-xs font-medium uppercase tracking-widest">{currentCommodity?.name} • Historical & Predicted Feed</p>
                                </div>

                                <div className="flex bg-slate-900/80 p-1.5 rounded-2xl border border-white/5">
                                    {[7, 30, 90].map(h => (
                                        <button
                                            key={h}
                                            onClick={() => setSelectedHorizon(h)}
                                            className={`px-4 py-2 rounded-xl text-xs font-black transition-all ${selectedHorizon === h ? 'bg-primary text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                                        >
                                            {h}D
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="h-[400px] w-full relative">
                                {loading && (
                                    <div className="absolute inset-0 bg-slate-950/20 backdrop-blur-[1px] flex items-center justify-center z-10 transition-all rounded-2xl">
                                        <Activity className="w-10 h-10 text-primary animate-spin" />
                                    </div>
                                )}
                                <ResponsiveContainer width="100%" height="100%">
                                    <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                            <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="4 4" stroke="#1e293b" vertical={false} opacity={0.6} />
                                        <XAxis
                                            dataKey="date"
                                            stroke="#475569"
                                            tick={{ fill: '#64748b', fontSize: 10, fontWeight: 700 }}
                                            tickMargin={15}
                                            minTickGap={40}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <YAxis
                                            domain={['auto', 'auto']}
                                            stroke="#475569"
                                            tick={{ fill: '#64748b', fontSize: 10, fontWeight: 700 }}
                                            tickFormatter={(v) => `$${v}`}
                                            axisLine={false}
                                            tickLine={false}
                                            orientation="right"
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: 'rgba(2, 6, 23, 0.9)',
                                                backdropFilter: 'blur(12px)',
                                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                                borderRadius: '12px',
                                                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                                                padding: '12px'
                                            }}
                                            itemStyle={{ fontSize: '12px', fontWeight: 800, padding: '2px 0' }}
                                            labelStyle={{ color: '#94a3b8', fontSize: '10px', fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}
                                            cursor={{ stroke: '#334155', strokeWidth: 1.5, strokeDasharray: '4 4' }}
                                        />

                                        {/* Confidence Bands */}
                                        <Area
                                            type="monotone"
                                            dataKey="upper"
                                            stroke="none"
                                            fill="#3b82f6"
                                            fillOpacity={0.03}
                                            animationDuration={1500}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="lower"
                                            stroke="none"
                                            fill="#020617"
                                            fillOpacity={0.6}
                                            animationDuration={1500}
                                        />

                                        {/* Main Price Line */}
                                        <Area
                                            type="monotone"
                                            dataKey="actual"
                                            stroke="#3b82f6"
                                            strokeWidth={3}
                                            fill="url(#colorActual)"
                                            activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
                                            animationDuration={1000}
                                        />

                                        {/* Prediction Line */}
                                        <Area
                                            type="monotone"
                                            dataKey="predicted"
                                            stroke="none"
                                            fill="url(#colorPredicted)"
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="predicted"
                                            stroke="#f59e0b"
                                            strokeWidth={3}
                                            strokeDasharray="6 6"
                                            dot={false}
                                            activeDot={{ r: 6, fill: '#f59e0b', stroke: '#fff', strokeWidth: 2 }}
                                            animationDuration={2000}
                                        />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>

                            <div className="mt-8 flex items-center justify-between">
                                <div className="flex items-center space-x-6">
                                    <div className="flex items-center text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                                        <div className="w-2 h-2 rounded-full bg-primary mr-2 shadow-[0_0_8px_rgba(59,130,246,0.6)]" /> Historical
                                    </div>
                                    <div className="flex items-center text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                                        <div className="w-2 h-2 rounded-full bg-warning mr-2 shadow-[0_0_8px_rgba(245,158,11,0.6)]" /> Estimated
                                    </div>
                                </div>
                                <div className="flex items-center bg-slate-900/50 p-1 rounded-xl">
                                    {['LSTM', 'ARIMA', 'LR', 'XGBoost'].map(m => {
                                        const actualName = m === 'LR' ? 'LinearRegression' : m;
                                        return (
                                            <button
                                                key={m}
                                                onClick={() => setSelectedModel(actualName)}
                                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black tracking-widest transition-all ${selectedModel === actualName ? 'bg-primary/20 text-primary' : 'text-gray-600 hover:text-gray-400'}`}
                                            >
                                                {m}
                                            </button>
                                        )
                                    })}
                                </div>
                            </div>

                            {/* Prediction Insight Box */}
                            {predictions.length > 0 && predictions[0].explanation && (
                                <div className="mt-6 p-6 rounded-2xl bg-primary/5 border border-primary/10 animate-in slide-in-from-bottom-4 duration-500">
                                    <div className="flex items-start space-x-4">
                                        <div className="p-2 bg-primary/20 rounded-lg">
                                            <Zap className="w-5 h-5 text-primary" />
                                        </div>
                                        <div>
                                            <h4 className="text-xs font-black uppercase tracking-widest text-primary mb-1">AI Forecast Analysis</h4>
                                            <p className="text-sm text-gray-300 leading-relaxed font-medium">
                                                {predictions[0].explanation}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Quick Stats Panel */}
                        <div className="grid grid-cols-3 gap-6">
                            <div className="glass-panel p-6 rounded-2xl flex flex-col items-center">
                                <DollarSign className="w-5 h-5 text-primary mb-2" />
                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Avg. Weekly</p>
                                <p className="text-white font-bold">$73.20</p>
                            </div>
                            <div className="glass-panel p-6 rounded-2xl flex flex-col items-center">
                                <TrendingUp className="w-5 h-5 text-emerald-500 mb-2" />
                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Volatility</p>
                                <p className="text-white font-bold">1.4%</p>
                            </div>
                            <div className="glass-panel p-6 rounded-2xl flex flex-col items-center">
                                <Activity className="w-5 h-5 text-amber-500 mb-2" />
                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Confidence</p>
                                <p className="text-white font-bold">Medium</p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}
