"use client"
import { useEffect, useState } from 'react'
import { getSentiment, NewsEvent } from '@/lib/api'
import { Newspaper, ArrowLeft, Clock, ExternalLink, TrendingUp, TrendingDown } from 'lucide-react'
import Link from 'next/link'

export default function NewsPage() {
    const [news, setNews] = useState<NewsEvent[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadNews() {
            try {
                const data = await getSentiment()
                setNews(data)
            } catch (e) {
                console.error("Failed to load news", e)
            } finally {
                setLoading(false)
            }
        }
        loadNews()
    }, [])

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-in fade-in duration-700">
            {/* Header */}
            <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <Link href="/" className="inline-flex items-center text-primary/60 hover:text-primary transition-colors mb-6 text-xs font-black uppercase tracking-widest group">
                        <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
                        Back to Intelligence Suite
                    </Link>
                    <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter flex items-center">
                        <Newspaper className="w-10 h-10 mr-4 text-primary" />
                        GLOBAL MARKET <span className="text-primary italic">INTEL</span>
                    </h1>
                    <p className="mt-4 text-gray-500 font-bold uppercase tracking-[0.2em] text-sm">Real-time Geopolitical & Economic Sentiment Stream</p>
                </div>
                
                <div className="bg-slate-900/50 border border-white/5 p-4 rounded-2xl flex items-center space-x-8">
                    <div className="text-center px-4">
                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-1">Active Signals</p>
                        <p className="text-white font-bold text-xl">{news.length}</p>
                    </div>
                    <div className="h-8 w-px bg-white/10" />
                    <div className="text-center px-4">
                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-1">Last Update</p>
                        <p className="text-white font-bold text-sm">JUST NOW</p>
                    </div>
                </div>
            </div>

            {/* News Feed */}
            <div className="space-y-6">
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-40">
                        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-6" />
                        <span className="text-gray-500 font-black text-sm tracking-widest uppercase">Deciphering Intelligence Channels...</span>
                    </div>
                ) : news.length > 0 ? (
                    <div className="grid grid-cols-1 gap-6">
                        {news.map((item) => (
                            <div 
                                key={item.id}
                                onClick={() => item.url && window.open(item.url, '_blank')}
                                className="group relative glass-panel p-8 rounded-3xl hover:bg-primary/5 transition-all duration-500 cursor-pointer border border-white/5 hover:border-primary/20 flex flex-col md:flex-row gap-8 items-start"
                            >
                                <div className="flex-1 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <span className="px-3 py-1 bg-white/5 rounded-lg text-[10px] font-black text-primary tracking-widest uppercase border border-white/5">
                                                {item.source || 'GLOBAL INTEL'}
                                            </span>
                                            <span className="text-[10px] text-gray-500 font-bold flex items-center italic">
                                                <Clock className="w-3 h-3 mr-1.5 opacity-50" />
                                                {new Date(item.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                            </span>
                                        </div>
                                        <div className={`p-2 rounded-xl ${item.sentiment_score > 0 ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
                                            {item.sentiment_score > 0 ? (
                                                <TrendingUp className="w-5 h-5 text-emerald-500" />
                                            ) : (
                                                <TrendingDown className="w-5 h-5 text-rose-500" />
                                            )}
                                        </div>
                                    </div>
                                    
                                    <h2 className="text-xl md:text-2xl font-bold text-white leading-tight group-hover:text-primary transition-colors">
                                        {item.headline}
                                    </h2>
                                    
                                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                        <div className="flex items-center space-x-4">
                                            <span className={`text-[10px] font-black uppercase tracking-widest flex items-center ${item.sentiment_score > 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                                <span className={`w-2 h-2 rounded-full mr-2 ${item.sentiment_score > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                                                Market Sentiment: {item.sentiment_score > 0 ? 'Bullish' : 'Bearish'}
                                            </span>
                                        </div>
                                        <button className="text-[10px] font-black uppercase tracking-widest text-primary/40 group-hover:text-primary flex items-center transition-all">
                                            Read Full Intelligence <ExternalLink className="w-3 h-3 ml-2" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="glass-panel p-20 rounded-3xl text-center border border-white/5 bg-slate-900/40">
                        <Newspaper className="w-16 h-16 text-gray-700 mx-auto mb-6 opacity-20" />
                        <h3 className="text-xl font-black text-gray-400 tracking-widest uppercase">No Intelligence Logged</h3>
                        <p className="text-sm text-gray-600 mt-2 font-bold uppercase tracking-widest">Scanning high-frequency channels for updates...</p>
                    </div>
                )}
            </div>
        </div>
    )
}
