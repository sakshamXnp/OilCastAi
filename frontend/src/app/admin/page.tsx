"use client"
import { useState, useEffect } from 'react'
import { getGlobalMetrics, trainModels, ModelMetric } from '@/lib/api'
import { Settings, Play, Server, Database, CheckCircle, Clock } from 'lucide-react'

export default function Admin() {
    const [metrics, setMetrics] = useState<ModelMetric[]>([])
    const [training, setTraining] = useState<Record<string, boolean>>({})
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadMetrics()
    }, [])

    async function loadMetrics() {
        try {
            const m = await getGlobalMetrics().catch(() => [])
            setMetrics(m)
        } finally {
            setLoading(false)
        }
    }

    const handleTrain = async (modelName: string) => {
        setTraining(prev => ({ ...prev, [modelName]: true }))
        try {
            await trainModels()
            // Visual mock for Training Wait Time in MVP (since actually training takes 1-2 mins in background)
            setTimeout(() => {
                setTraining(prev => ({ ...prev, [modelName]: false }))
                loadMetrics()
            }, 5000)
        } catch {
            setTraining(prev => ({ ...prev, [modelName]: false }))
        }
    }

    return (
        <div className="space-y-8 max-w-5xl mx-auto">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white mb-2 flex items-center">
                    <Settings className="w-8 h-8 mr-3 text-gray-400" />
                    System Administration
                </h1>
                <p className="text-gray-400">Manage machine learning pipelines, review performance, and execute dynamic retraining commands.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-panel p-6 rounded-2xl flex items-center justify-between hover:border-primary/50 transition-colors">
                    <div className="flex items-center">
                        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mr-4 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
                            <Database className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white">Database Status</h3>
                            <p className="text-sm text-gray-400">PostgreSQL 15 Operational</p>
                        </div>
                    </div>
                    <CheckCircle className="w-6 h-6 text-accent drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                </div>

                <div className="glass-panel p-6 rounded-2xl flex items-center justify-between hover:border-accent/50 transition-colors">
                    <div className="flex items-center">
                        <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center mr-4 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                            <Server className="w-6 h-6 text-accent" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white">API Health</h3>
                            <p className="text-sm text-gray-400">Auto-Maintenance Thread Active</p>
                        </div>
                    </div>
                    <CheckCircle className="w-6 h-6 text-accent drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                </div>
            </div>

            <div className="glass-panel rounded-2xl overflow-hidden hover:border-gray-600 transition-colors">
                <div className="p-6 border-b border-gray-800 bg-secondary/30">
                    <h2 className="text-xl font-bold text-white">Pipeline Execution Commands</h2>
                    <p className="text-sm text-gray-400 mt-1">Trigger manual evaluations and retraining protocols down to the model level.</p>
                </div>

                <div className="p-6 space-y-6">
                    {['LSTM', 'ARIMA', 'LinearRegression'].map(modelName => {
                        const m = metrics.find(x => x.model_name === modelName)
                        const isTraining = training[modelName]

                        return (
                            <div key={modelName} className="group flex flex-col md:flex-row items-center justify-between p-6 bg-[#0f172a] rounded-xl border border-gray-800 hover:border-gray-700 transition-colors shadow-sm">
                                <div className="mb-4 md:mb-0 w-full md:w-auto">
                                    <h4 className="font-bold text-white text-lg tracking-wide">{modelName}</h4>
                                    {m ? (
                                        <div className="flex flex-wrap items-center mt-3 gap-3">
                                            <span className="text-sm border border-gray-700 bg-secondary/50 px-3 py-1.5 rounded-lg text-gray-300 shadow-sm font-medium">
                                                RMSE <span className="text-white ml-1">{m.rmse.toFixed(2)}</span>
                                            </span>
                                            <span className="text-sm border border-gray-700 bg-secondary/50 px-3 py-1.5 rounded-lg text-gray-300 shadow-sm font-medium">
                                                MAPE <span className="text-white ml-1">{(m.mape * 100).toFixed(2)}%</span>
                                            </span>
                                            <span className="text-xs text-gray-500 flex items-center font-medium bg-black/20 px-3 py-1.5 rounded-lg">
                                                <Clock className="w-3.5 h-3.5 mr-1.5" />
                                                {new Date(m.last_trained).toLocaleString()}
                                            </span>
                                        </div>
                                    ) : (
                                        <span className="text-sm font-medium text-warning mt-2 block bg-warning/10 border border-warning/20 px-3 py-1.5 rounded-lg inline-block">Pending Initial Training Execution</span>
                                    )}
                                </div>

                                <button
                                    onClick={() => handleTrain(modelName)}
                                    disabled={isTraining}
                                    className={`flex items-center px-6 py-3 rounded-lg font-bold transition-all w-full md:w-auto justify-center ${isTraining
                                        ? 'bg-gray-800 text-gray-400 cursor-not-allowed border border-gray-700'
                                        : 'bg-primary hover:bg-primary/90 text-white shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.4)] border border-transparent'
                                        }`}
                                >
                                    {isTraining ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mr-3"></div>
                                            Executing...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-5 h-5 mr-2 fill-current" />
                                            Execute Training
                                        </>
                                    )}
                                </button>
                            </div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
