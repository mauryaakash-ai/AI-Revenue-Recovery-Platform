import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import { AppShell } from '../../components/layout/AppShell'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Sliders,
  TrendingDown,
  TrendingUp,
  ShieldAlert,
  Server,
  Zap
} from 'lucide-react'

interface BankHealth {
  bank_code: string
  bank_name: string
  success_rate: number
  failure_rate: number
  timeout_rate: number
  avg_latency_ms: number
  anomaly_score: number
  incident_status: string
  recommended_action: string
  last_updated: string
}

interface GatewayHealth {
  gateway_id: string
  gateway_name: string
  success_rate: number
  failure_rate: number
  timeout_rate: number
  avg_latency_ms: number
  anomaly_score: number
  incident_status: string
  recommended_action: string
}

export default function BankHealthPage() {
  const [banks, setBanks] = useState<BankHealth[]>([])
  const [gateways, setGateways] = useState<GatewayHealth[]>([])
  const [loading, setLoading] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [selectedBank, setSelectedBank] = useState('State Bank of India')
  const [simSpike, setSimSpike] = useState('0.25')
  const [simLatency, setSimLatency] = useState('1450')
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null)

  const fetchHealth = async () => {
    try {
      setLoading(true)
      const baseUrl = 'http://localhost:8000/api/v1'
      const [bankRes, gwRes] = await Promise.all([
        fetch(`${baseUrl}/banks/health`),
        fetch(`${baseUrl}/gateways/health`)
      ])
      if (bankRes.ok) {
        const bData = await bankRes.json()
        setBanks(bData.banks || [])
      }
      if (gwRes.ok) {
        const gData = await gwRes.json()
        setGateways(gData.gateways || [])
      }
    } catch (e) {
      console.error('Error fetching health data', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  const handleSimulateIncident = async () => {
    try {
      setSimulating(true)
      setFeedbackMsg(null)
      const res = await fetch('http://localhost:8000/api/v1/banks/health/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bank_name: selectedBank,
          failure_rate_spike: parseFloat(simSpike) || 0.25,
          avg_latency_ms: parseFloat(simLatency) || 1450.0,
          status: 'DEGRADED'
        })
      })
      const data = await res.json()
      setFeedbackMsg(data.advisory || 'Degradation incident applied.')
      fetchHealth()
    } catch (e: any) {
      setFeedbackMsg(`Simulation error: ${e.message}`)
    } finally {
      setSimulating(false)
    }
  }

  return (
    <AppShell>
      <Head>
        <title>Bank & Gateway Real-Time Health | RevPilot</title>
      </Head>

      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Bank & Gateway Telemetry</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Real-time degradation anomaly detection, retry throttling advisory, and smart payment rerouting.
              </p>
            </div>
          </div>
          <button
            onClick={fetchHealth}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </button>
        </div>

        {/* Advisory banner if incident is active */}
        {feedbackMsg && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-900 space-y-1">
              <span className="font-bold">Automated Risk Advisory Triggered:</span>
              <p>{feedbackMsg}</p>
            </div>
          </div>
        )}

        {/* Banks Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-900">Issuer Core Banking Systems (India)</h2>
            <span className="text-[11px] text-slate-400 font-medium">Auto-updated via live telemetry</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {banks.map((b) => (
              <div
                key={b.bank_name}
                className={`p-5 rounded-2xl border transition shadow-xs ${
                  b.incident_status === 'DEGRADED'
                    ? 'bg-amber-50/40 border-amber-200 ring-1 ring-amber-300'
                    : 'bg-white border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{b.bank_name}</h3>
                    <span className="text-[10px] text-slate-400 font-mono font-medium">{b.bank_code}</span>
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      b.incident_status === 'HEALTHY'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-100 text-amber-800 border border-amber-300 animate-pulse'
                    }`}
                  >
                    {b.incident_status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-slate-50 p-2.5 rounded-xl">
                    <span className="text-[10px] font-semibold text-slate-400 block">Success Rate</span>
                    <span className="text-sm font-bold text-slate-900">{(b.success_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl">
                    <span className="text-[10px] font-semibold text-slate-400 block">Avg Latency</span>
                    <span className="text-sm font-bold text-slate-900">{b.avg_latency_ms.toFixed(0)} ms</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl">
                    <span className="text-[10px] font-semibold text-slate-400 block">Failure Spike</span>
                    <span className="text-sm font-bold text-red-600">{(b.failure_rate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="bg-slate-50 p-2.5 rounded-xl">
                    <span className="text-[10px] font-semibold text-slate-400 block">Anomaly Index</span>
                    <span className={`text-sm font-bold ${b.anomaly_score > 30 ? 'text-amber-600' : 'text-slate-700'}`}>
                      {b.anomaly_score.toFixed(1)}/100
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500 text-[11px]">Recommended Policy:</span>
                  <span
                    className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                      b.recommended_action === 'THROTTLE_RETRIES'
                        ? 'bg-red-50 text-red-700 font-semibold'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {b.recommended_action}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gateways Section */}
        <div>
          <h2 className="text-sm font-bold text-slate-900 mb-3">Payment Gateway Switches</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {gateways.map((g) => (
              <div key={g.gateway_id} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900">{g.gateway_name}</span>
                  <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                    {g.incident_status}
                  </span>
                </div>
                <div className="flex items-baseline justify-between text-xs pt-1">
                  <span className="text-slate-400 text-[11px]">Success:</span>
                  <span className="font-bold text-slate-800">{(g.success_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-baseline justify-between text-xs">
                  <span className="text-slate-400 text-[11px]">Latency:</span>
                  <span className="font-semibold text-slate-600">{g.avg_latency_ms} ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Incident Simulator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Sliders className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Simulate Bank Incident & Observe Autonomous Throttling</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Target Issuer Bank</label>
              <select
                value={selectedBank}
                onChange={(e) => setSelectedBank(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
              >
                <option value="State Bank of India">State Bank of India (SBI)</option>
                <option value="HDFC Bank">HDFC Bank</option>
                <option value="ICICI Bank">ICICI Bank</option>
                <option value="Axis Bank">Axis Bank</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Failure Rate Spike (e.g. 0.25 = 25%)</label>
              <input
                type="number"
                step="0.05"
                value={simSpike}
                onChange={(e) => setSimSpike(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Latency Spike (ms)</label>
              <input
                type="number"
                value={simLatency}
                onChange={(e) => setSimLatency(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
              />
            </div>
          </div>

          <button
            onClick={handleSimulateIncident}
            disabled={simulating}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-xs transition disabled:opacity-50"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{simulating ? 'Simulating Anomaly...' : 'Trigger Simulated Bank Outage / Spike'}</span>
          </button>
        </div>
      </div>
    </AppShell>
  )
}

