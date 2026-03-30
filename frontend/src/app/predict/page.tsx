"use client"
import { useEffect, useState } from 'react'
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, ComposedChart } from 'recharts'
import { getPredictions, getMetrics, Prediction, ModelMetric } from '@/lib/api'
import { BrainCircuit, AlertTriangle, ShieldCheck } from 'lucide-react'

export default function Predictions() {
    const [predictions, setPredictions] = useState<Record<string, Prediction[]>>({})
    const [metrics, setMetrics] = useState<ModelMetric[]>([])
    const [selectedModel, setSelectedModel] = useState<string>('LSTM')
    const [selectedOil, setSelectedOil] = useState<string>('WTI')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadData() {
            setLoading(true)
            try {
                const models = ['LinearRegression', 'ARIMA', 'LSTM']
                const predsList = await Promise.all(models.map(m => getPredictions(selectedOil, m, 30).catch(() => [])))

                const predsMap: Record<string, Prediction[]> = {}
                models.forEach((m, i) => predsMap[m] = predsList[i])

                setPredictions(predsMap)

                const m = await getMetrics(selectedOil).catch(() => [])
                setMetrics(m)
            } catch (e) {
                console.error("Error loading prediction data:", e)
            } finally {
                setLoading(false)
            }
        }
        loadData()
    }, [selectedOil])

    const currentMetrics = metrics.find(m => m.model_name === selectedModel)
    const chartData = (predictions[selectedModel] || []).map(p => ({
        date: new Date(p.target_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        predicted: parseFloat(p.predicted_price.toFixed(2)),
        lower: p.confidence_lower ? parseFloat(p.confidence_lower.toFixed(2)) : null,
        upper: p.confidence_upper ? parseFloat(p.confidence_upper.toFixed(2)) : null
    }))

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white flex items-center shadow-black drop-shadow-md">
                        <BrainCircuit className="w-8 h-8 mr-3 text-primary" />
                        AI Forecasting
                    </h1>
                    <p className="text-gray-400 mt-1">30-day ahead projections with confidence intervals</p>
                </div>

                <div className="flex items-center space-x-4">
                    <select
                        value={selectedOil}
                        onChange={(e) => setSelectedOil(e.target.value)}
                        className="bg-secondary/50 border border-primary/30 text-white text-sm rounded-full px-4 py-2 outline-none focus:ring-2 focus:ring-primary/50 transition-all cursor-pointer"
                    >
                        <option value="CL=F">WTI Crude Oil</option>
                        <option value="BZ=F">Brent Crude Oil</option>
                    </select>

                    <div className="flex bg-secondary/50 p-1 rounded-xl border border-gray-800 shadow-inner">
                        {['LSTM', 'ARIMA', 'LinearRegression'].map(m => (
                            <button
                                key={m}
                                onClick={() => setSelectedModel(m)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedModel === m ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:text-white'}`}
                            >
                                {m === 'LinearRegression' ? 'Linear Reg' : m}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Metrics Sidebar */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-2xl border-t-4 border-t-primary shadow-[0_4px_20px_rgba(0,0,0,0.3)] hover:border-t-accent transition-all duration-300">
                        <h3 className="text-lg font-bold text-white mb-4">Model Performance</h3>
                        {currentMetrics ? (
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400 font-medium font-mono text-xs uppercase tracking-wider">RMSE</span>
                                        <span className="text-white font-bold">{currentMetrics.rmse.toFixed(3)}</span>
                                    </div>
                                    <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                        <div
                                            className="bg-primary h-full rounded-full shadow-[0_0_10px_rgba(59,130,246,0.6)] transition-all duration-1000"
                                            style={{ width: `${Math.max(5, 100 - (currentMetrics.rmse * 10))}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-400 font-medium font-mono text-xs uppercase tracking-wider">MAE</span>
                                        <span className="text-white font-bold">{currentMetrics.mae.toFixed(3)}</span>
                                    </div>
                                    <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                                        <div
                                            className="bg-accent h-full rounded-full shadow-[0_0_10px_rgba(16,185,129,0.6)] transition-all duration-1000"
                                            style={{ width: `${Math.max(5, 100 - (currentMetrics.mae * 10))}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div className="pt-2">
                                    <div className="flex justify-between text-sm items-center">
                                        <span className="text-gray-400 font-medium font-mono text-xs uppercase tracking-wider">MAPE</span>
                                        <div className="bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
                                            <span className="text-primary font-bold">{(currentMetrics.mape * 100).toFixed(2)}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-10 text-gray-500 opacity-60">
                                <AlertTriangle className="w-10 h-10 mb-3 text-warning/50" />
                                <span className="text-sm font-medium">Metrics syncing...</span>
                            </div>
                        )}
                    </div>

                    <div className="glass-panel p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent border border-white/5">
                        <div className="flex items-start">
                            <ShieldCheck className="w-6 h-6 text-primary mr-3 flex-shrink-0" />
                            <div>
                                <h4 className="font-semibold text-white mb-1.5">95% Confidence Interval</h4>
                                <p className="text-sm text-gray-400 leading-relaxed text-pretty">
                                    The shaded boundary represents the dynamic volatility forecast for <span className="text-primary font-semibold">{selectedOil}</span> based on {selectedModel} probabilistic output.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Chart */}
                <div className="glass-panel p-6 rounded-2xl lg:col-span-2 h-[520px] flex flex-col hover:border-gray-700/50 transition-all shadow-xl group">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-xl font-bold text-white tracking-wide">30-Day {selectedOil} Forecast</h2>
                            <p className="text-xs text-gray-500 mt-0.5">Algorithm: {selectedModel}</p>
                        </div>
                        <div className="flex items-center space-x-4 bg-secondary/30 px-3 py-1.5 rounded-lg border border-white/5">
                            <div className="flex items-center text-[10px] text-gray-400 font-bold uppercase tracking-widest">
                                <span className="w-2.5 h-2.5 bg-primary rounded-full mr-2 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></span>
                                Projection
                            </div>
                        </div>
                    </div>

                    <div className="flex-1 w-full relative">
                        {loading ? (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="relative">
                                    <div className="w-12 h-12 border-4 border-primary/20 rounded-full"></div>
                                    <div className="absolute top-0 w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                                </div>
                            </div>
                        ) : chartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="predGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="4 4" stroke="#1e293b" vertical={false} opacity={0.6} />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#475569"
                                        tick={{ fill: '#64748b', fontSize: 11, fontWeight: 700 }}
                                        tickMargin={12}
                                        minTickGap={30}
                                        axisLine={false}
                                        tickLine={false}
                                    />
                                    <YAxis
                                        domain={['auto', 'auto']}
                                        stroke="#475569"
                                        tick={{ fill: '#64748b', fontSize: 11, fontWeight: 700 }}
                                        tickFormatter={(val) => `$${val}`}
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
                                            color: '#f8fafc'
                                        }}
                                        itemStyle={{ color: '#e2e8f0', fontWeight: 800, fontSize: '13px' }}
                                        labelStyle={{ color: '#94a3b8', marginBottom: '8px', fontWeight: 900, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.1em' }}
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

                                    {/* Prediction Main Line */}
                                    <Area
                                        type="monotone"
                                        dataKey="predicted"
                                        stroke="none"
                                        fill="url(#predGradient)"
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="predicted"
                                        stroke="#3b82f6"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
                                        activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
                                        animationDuration={2000}
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 bg-secondary/10 rounded-xl border border-white/5 border-dashed">
                                <AlertTriangle className="w-12 h-12 mb-4 text-warning opacity-30" />
                                <p className="text-sm font-medium">No {selectedModel} predictions found for {selectedOil}.</p>
                                <p className="text-xs mt-1 text-gray-600 font-mono">Run training cycle in Admin Tools</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
