const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const API_URL = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL;

export interface Commodity {
    id: number;
    name: string;
    symbol: string;
    category: string;
    region: string | null;
}

export interface PriceData {
    id: number;
    commodity_id: number;
    price: number;
    timestamp: string;
    source: string;
}

export interface Prediction {
    id: number;
    commodity_id: number;
    model_name: string;
    target_date: string;
    predicted_price: number;
    confidence_lower: number | null;
    confidence_upper: number | null;
    horizon_days: number;
    explanation: string | null;
    metrics_json: string | null;
}

export interface ModelMetric {
    id: number;
    commodity_id: number;
    model_name: string;
    rmse: number;
    mae: number;
    mape: number;
    last_trained: string;
}

export interface NewsEvent {
    id: number;
    headline: string;
    source: string | null;
    url: string | null;
    sentiment_score: number;
    timestamp: string;
}

export async function getCommodities(): Promise<Commodity[]> {
    const res = await fetch(`${API_URL}/commodities`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch commodities');
    return res.json();
}

export async function getHistory(symbol: string, days: number = 30): Promise<PriceData[]> {
    const res = await fetch(`${API_URL}/prices/${symbol}?days=${days}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch history for ${symbol}`);
    return res.json();
}

export async function getPredictions(symbol: string, model: string = 'LSTM', horizon: number = 30): Promise<Prediction[]> {
    const res = await fetch(`${API_URL}/predict/${symbol}?model=${model}&horizon=${horizon}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch predictions for ${symbol}`);
    return res.json();
}

export async function getMetrics(symbol: string): Promise<ModelMetric[]> {
    const res = await fetch(`${API_URL}/model/metrics/${symbol}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch metrics for ${symbol}`);
    return res.json();
}

export async function getGlobalMetrics(): Promise<ModelMetric[]> {
    const res = await fetch(`${API_URL}/model/metrics`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch global metrics');
    return res.json();
}

export async function getSentiment(): Promise<NewsEvent[]> {
    const res = await fetch(`${API_URL}/sentiment`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch sentiment');
    return res.json();
}

export async function getSentimentScore(): Promise<{ score: number; status: string }> {
    const res = await fetch(`${API_URL}/sentiment/score`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch sentiment score');
    return res.json();
}

export async function getLatestPrices(): Promise<any[]> {
    const res = await fetch(`${API_URL}/latest-prices`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch latest prices');
    return res.json();
}

export async function trainModels(symbol?: string): Promise<{ message: string }> {
    const url = symbol ? `${API_URL}/model/train?commodity_symbol=${symbol}` : `${API_URL}/model/train`;
    const res = await fetch(url, { method: 'POST', cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to start training');
    return res.json();
}

export interface OilPriceEntry {
    symbol: string;
    name: string;
    price: number;
    change: number;
    change_pct: number;
    timestamp: string | null;
    region: string | null;
    has_data: boolean;
}

export interface OilPricesGrouped {
    futures_indexes: OilPriceEntry[];
    opec_members: OilPriceEntry[];
    international: OilPriceEntry[];
    canadian_blends: OilPriceEntry[];
    us_blends: OilPriceEntry[];
}

export async function getOilPrices(): Promise<OilPricesGrouped> {
    const res = await fetch(`${API_URL}/oil-prices`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch oil prices');
    return res.json();
}
