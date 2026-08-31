import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  Layers, Sparkles, CheckCircle2, ArrowRight, Plus, ToggleLeft, ToggleRight, Shield, Sliders, Loader2
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function StrategyBuilderPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<any>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Form State for new strategy
  const [newStrategy, setNewStrategy] = useState({
    name: 'Smart UPI Weekend Booster',
    description: 'Auto-recovers weekend transaction drops with instant WhatsApp deep-link',
    wait_delay_minutes: 60,
    max_retries: 3,
    min_amount: 500,
    max_amount: 100000,
    retry_methods: ['upi', 'card'],
    communication_channels: ['whatsapp']
  })

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/strategies`)
      setData(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStrategies()
  }, [merchantId])

  const handleToggle = async (strategyId: string) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/strategies/${strategyId}/toggle`)
      loadStrategies()
    } catch (err: any) {
      alert('Failed: ' + err.message)
    }
  }

  const handleApplyAiSuggestion = async () => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/strategies/apply-ai-suggestion`)
      alert(res.data.message || 'AI Strategy applied!')
      loadStrategies()
    } catch (err: any) {
      alert('Failed to apply AI strategy: ' + err.message)
    }
  }

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await axios.post(`${baseUrl}/api/v1/merchants/${merchantId}/strategies`, newStrategy)
      setShowCreateModal(false)
      loadStrategies()
    } catch (err: any) {
      alert('Failed: ' + err.message)
    }
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Recovery Strategy Builder</h1>
          <p className="text-xs text-slate-500 mt-1">
            Build, configure, and optimize dynamic recovery flows, smart delay windows, and multi-channel triggers.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition"
        >
          <Plus className="w-3.5 h-3.5" />
          Create New Strategy
        </button>
      </div>

      {loading && !data ? (
        <div className="py-24 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-3 text-xs text-slate-500">Loading active recovery policy engines...</p>
        </div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Section 29: AI Strategy Suggestion Panel */}
          {data?.ai_suggestion && (
            <div className="bg-gradient-to-r from-blue-50/90 via-indigo-50/50 to-white rounded-xl border border-blue-200 p-6 shadow-xs">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-3.5">
                  <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700">AI Strategy Optimization</span>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono">
                        +{data.ai_suggestion.incremental_revenue}
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-900 mt-1 leading-relaxed">
                      {data.ai_suggestion.summary}
                    </p>
                    <div className="mt-3 space-y-1">
                      {data.ai_suggestion.recommended_changes?.map((c: string, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 text-xs text-slate-700">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span>{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0 pl-13 md:pl-0">
                  <button
                    onClick={handleApplyAiSuggestion}
                    className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Apply Suggestion
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Strategies Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.strategies?.map((strat: any) => (
              <div key={strat.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      strat.is_active ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {strat.is_active ? 'Active Flow' : 'Disabled'}
                    </span>
                    <button
                      onClick={() => handleToggle(strat.id)}
                      className="text-slate-400 hover:text-slate-700 p-1"
                    >
                      {strat.is_active ? (
                        <ToggleRight className="w-6 h-6 text-emerald-600" />
                      ) : (
                        <ToggleLeft className="w-6 h-6 text-slate-300" />
                      )}
                    </button>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 mt-3">{strat.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{strat.description}</p>

                  <div className="mt-4 space-y-2 text-xs border-t border-slate-100 pt-3">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Wait Delay Window:</span>
                      <span className="font-semibold text-slate-800">{strat.wait_delay_minutes} minutes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max Retry Attempts:</span>
                      <span className="font-semibold text-slate-800">{strat.max_retries} attempts</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Channels:</span>
                      <span className="font-semibold text-slate-800 uppercase">{strat.communication_channels.join(', ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Optimized Recovery:</span>
                      <span className="font-bold text-emerald-700">{Math.round(strat.recovery_rate_optimized * 100)}%</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Baseline: {Math.round(strat.recovery_rate_baseline * 100)}%</span>
                  <button
                    onClick={() => alert(`Configuring parameters for ${strat.name}`)}
                    className="font-semibold text-blue-600 hover:underline"
                  >
                    Configure Policy
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6">
            <h3 className="text-base font-bold text-slate-900 mb-1">Create Recovery Strategy</h3>
            <p className="text-xs text-slate-500 mb-4">Define automated triggers, wait windows, and notification channels.</p>

            <form onSubmit={handleCreateSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Strategy Name</label>
                <input
                  type="text"
                  value={newStrategy.name}
                  onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Description</label>
                <input
                  type="text"
                  value={newStrategy.description}
                  onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Cooldown Delay (Mins)</label>
                  <input
                    type="number"
                    value={newStrategy.wait_delay_minutes}
                    onChange={(e) => setNewStrategy({ ...newStrategy, wait_delay_minutes: Number(e.target.value) })}
                    className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Max Retries</label>
                  <input
                    type="number"
                    value={newStrategy.max_retries}
                    onChange={(e) => setNewStrategy({ ...newStrategy, max_retries: Number(e.target.value) })}
                    className="w-full p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 rounded border border-slate-200 text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700"
                >
                  Save Strategy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  )
}

