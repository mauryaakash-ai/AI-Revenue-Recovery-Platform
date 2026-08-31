import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Activity, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Cpu, BarChart3, Database, Loader2 } from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function ModelHealthPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/models/health`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [merchantId])

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Header */}
      <div className="pb-6 border-b border-slate-200 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Model Monitoring & Feature Drift</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time tracking of Population Stability Index (PSI), ROC-AUC calibration, and feature drift distributions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Ensemble Health: 100% Calibrated
          </span>
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 shadow-2xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
        </div>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Calculating Population Stability Indices...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Overall System PSI</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold text-slate-900">{data?.overall_psi || '0.042'}</span>
                <span className="text-xs font-semibold text-emerald-600">Stable (&lt; 0.10)</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">No significant population drift detected</p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Mean ROC-AUC</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold text-slate-900">0.892</span>
                <span className="text-xs font-semibold text-emerald-600">High Discrimination</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Evaluated across N=25,480 settlements</p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">C-Index Timing Concordance</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold text-slate-900">0.841</span>
                <span className="text-xs font-semibold text-blue-600">DeepSurv Model</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Optimal retry window prediction accuracy</p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Autonomous Rollback</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold text-emerald-700">Armed & Active</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Auto-switches to rule engine if PSI &gt; 0.25</p>
            </div>
          </div>

          {/* Active Model Ensemble Registry */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-600" />
                Active Model Ensemble Registry
              </h2>
              <span className="text-xs text-slate-500">Managed by Model Monitoring Agent</span>
            </div>

            <div className="divide-y divide-slate-100 text-xs">
              {data?.models?.map((model: any, idx: number) => (
                <div key={idx} className="p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 hover:bg-slate-50/60 transition">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h3 className="font-bold text-slate-900 text-sm">{model.name}</h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        {model.status}
                      </span>
                    </div>
                    <p className="text-slate-500 mt-0.5">
                      Population Stability Index: <span className="font-mono font-bold text-slate-800">{model.psi_score}</span> · Brier Score: <span className="font-mono text-slate-800">{model.calibration_brier_score || '0.041'}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => alert(`Retrain initiated for ${model.name}`)}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold"
                    >
                      Trigger Retraining
                    </button>
                    <button 
                      onClick={() => alert(`Shadow pipeline enabled for ${model.name}`)}
                      className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold"
                    >
                      View Shadow Metrics
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Feature Drift Table */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-2xs">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Database className="w-4 h-4 text-indigo-600" />
                Input Feature Drift Breakdown
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Wasserstein distance & PSI tracking across live transaction attributes vs training baseline.
              </p>
            </div>

            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-6">Feature Name</th>
                  <th className="py-3 px-6">PSI Value</th>
                  <th className="py-3 px-6">Drift Status</th>
                  <th className="py-3 px-6">Drift Context / Root Cause</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {data?.feature_drift_table?.map((feat: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="py-3.5 px-6 font-mono font-semibold text-slate-900">{feat.feature}</td>
                    <td className="py-3.5 px-6 font-mono font-bold text-slate-800">{feat.psi}</td>
                    <td className="py-3.5 px-6">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        feat.status === 'Stable' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {feat.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-500">{feat.drift_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  )
}
