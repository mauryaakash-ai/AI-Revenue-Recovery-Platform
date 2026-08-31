import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  FlaskConical, Sparkles, TrendingUp, CheckCircle2, Plus, ArrowUpRight, Loader2
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function ExperimentsPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)

  const loadExperiments = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/experiments`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadExperiments()
  }, [merchantId])

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Recovery Experiments (A/B Testing)</h1>
          <p className="text-xs text-slate-500 mt-1">
            Statistically validated multi-variant testing for recovery timing, channel priority, and messaging hooks.
          </p>
        </div>

        <button
          onClick={() => alert('Experiment designer initialized.')}
          className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition"
        >
          <Plus className="w-3.5 h-3.5" />
          Launch New A/B Test
        </button>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Computing statistical significance & p-values...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {data?.experiments?.map((exp: any) => (
            <div key={exp.id} className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-slate-900">{exp.name}</h3>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {exp.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5"><span className="font-semibold text-slate-700">Hypothesis:</span> {exp.hypothesis}</p>
                </div>

                <div className="text-right text-xs">
                  <span className="text-slate-400">Sample size:</span> <span className="font-semibold text-slate-900">{exp.sample_size?.toLocaleString()} checkouts</span>
                </div>
              </div>

              {/* Variant Comparison Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Control */}
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-700">Control (A) — {exp.control?.name}</span>
                    <span className="text-xs font-mono font-bold text-slate-900">{Math.round(exp.control?.conversion_rate * 100)}% Conversion</span>
                  </div>
                  <div className="mt-2 w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div className="bg-slate-500 h-full rounded-full" style={{ width: `${exp.control?.conversion_rate * 100}%` }} />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2">{exp.control?.conversions} successful recoveries</p>
                </div>

                {/* Variant */}
                <div className="p-4 rounded-lg bg-blue-50/50 border border-blue-200">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-blue-900">Variant (B) — {exp.variant?.name}</span>
                    <span className="text-xs font-mono font-bold text-emerald-700">{Math.round(exp.variant?.conversion_rate * 100)}% Conversion</span>
                  </div>
                  <div className="mt-2 w-full bg-blue-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${exp.variant?.conversion_rate * 100}%` }} />
                  </div>
                  <p className="text-[11px] text-blue-700 mt-2 font-medium">{exp.variant?.conversions} successful recoveries</p>
                </div>
              </div>

              {/* Confidence & Uplift Bar */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-emerald-700 flex items-center gap-1">
                    <ArrowUpRight className="w-4 h-4" />
                    +{exp.uplift_pct}% Conversion Uplift
                  </span>
                  <span className="text-slate-300">|</span>
                  <span className="font-semibold text-slate-800">
                    Confidence: {exp.statistical_confidence}% (p &lt; 0.05)
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-500 font-medium">Winner: <span className="font-bold text-slate-900">{exp.winner}</span></span>
                  <button
                    onClick={() => alert(`Deployed ${exp.winner} as 100% default policy.`)}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold transition"
                  >
                    Deploy Variant to 100% Traffic
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  )
}

