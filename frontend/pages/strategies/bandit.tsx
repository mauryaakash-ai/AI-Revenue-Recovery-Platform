import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import { AppShell } from '../../components/layout/AppShell'
import {
  Cpu,
  RefreshCw,
  Power,
  TrendingUp,
  Percent,
  Coins,
  ShieldCheck,
  AlertOctagon,
  Sparkles,
  BarChart3
} from 'lucide-react'

interface BanditArm {
  name: string
  label: string
  pulls: number
  conversions: number
  conversion_rate: number
  total_reward: number
  average_reward: number
  base_cost: number
  ucb_score: number
  is_active: boolean
}

export default function BanditRLPage() {
  const [arms, setArms] = useState<BanditArm[]>([])
  const [totalPulls, setTotalPulls] = useState(0)
  const [algorithm, setAlgorithm] = useState('')
  const [loading, setLoading] = useState(false)
  const [togglingArm, setTogglingArm] = useState<string | null>(null)

  const fetchBanditStatus = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:8000/api/v1/bandit/arms')
      if (res.ok) {
        const data = await res.json()
        setArms(data.arms || [])
        setTotalPulls(data.total_bandit_pulls || 0)
        setAlgorithm(data.algorithm || 'UCB1 Exploration')
      }
    } catch (e) {
      console.error('Failed to load bandit data', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBanditStatus()
  }, [])

  const handleToggleKillSwitch = async (armName: string, currentActive: boolean) => {
    try {
      setTogglingArm(armName)
      const res = await fetch('http://localhost:8000/api/v1/bandit/kill-switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          arm_name: armName,
          active: !currentActive
        })
      })
      if (res.ok) {
        fetchBanditStatus()
      }
    } catch (e) {
      console.error('Failed to toggle kill switch', e)
    } finally {
      setTogglingArm(null)
    }
  }

  return (
    <AppShell>
      <Head>
        <title>Contextual Multi-Armed Bandit RL | RevPilot</title>
      </Head>

      <div className="space-y-6 max-w-7xl mx-auto pb-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Multi-Armed Bandit Reinforcement Learning</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Dynamic exploration vs exploitation balancing recovery channels based on Net Recovered Revenue.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchBanditStatus}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh Stats</span>
            </button>
          </div>
        </div>

        {/* Algorithm Metrics Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Active Algorithm</span>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span className="text-sm font-bold text-slate-900">UCB1 (C=1.414)</span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1 block">Upper Confidence Bound</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Cumulative Bandit Pulls</span>
            <span className="text-xl font-extrabold text-slate-900">{totalPulls.toLocaleString()}</span>
            <span className="text-[11px] text-slate-500 mt-1 block">Live decision actions</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Active Arms</span>
            <span className="text-xl font-extrabold text-emerald-600">
              {arms.filter((a) => a.is_active).length} / {arms.length}
            </span>
            <span className="text-[11px] text-slate-500 mt-1 block">Experimentation arms</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Safety Constraints</span>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold text-slate-900">Instant Kill Switch</span>
            </div>
            <span className="text-[11px] text-slate-500 mt-1 block">Policy overrides & limits</span>
          </div>
        </div>

        {/* Arms Grid */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-900">Recovery Strategy Action Space (8 Arms)</h2>
            <span className="text-[11px] text-slate-400">Click power icon to safely kill/enable any arm</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {arms.map((arm) => (
              <div
                key={arm.name}
                className={`p-5 rounded-2xl border transition shadow-xs flex flex-col justify-between ${
                  !arm.is_active
                    ? 'bg-slate-100 border-slate-300 opacity-60'
                    : 'bg-white border-slate-200 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 border-b border-slate-100 pb-3 mb-3">
                    <div>
                      <h3 className="text-xs font-bold text-slate-900 line-clamp-1">{arm.label}</h3>
                      <span className="text-[10px] font-mono text-slate-400">{arm.name}</span>
                    </div>
                    <button
                      onClick={() => handleToggleKillSwitch(arm.name, arm.is_active)}
                      disabled={togglingArm === arm.name}
                      title={arm.is_active ? 'Click to Kill Arm' : 'Click to Enable Arm'}
                      className={`p-1.5 rounded-lg border transition ${
                        arm.is_active
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-red-50 hover:text-red-700 hover:border-red-200'
                          : 'bg-slate-200 text-slate-600 border-slate-300 hover:bg-emerald-50 hover:text-emerald-700'
                      }`}
                    >
                      <Power className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Conversion Rate:</span>
                      <span className="font-bold text-slate-900">{(arm.conversion_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Avg Net Reward:</span>
                      <span className="font-bold text-emerald-600">₹{arm.average_reward.toFixed(0)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Exploration Score:</span>
                      <span className="font-mono font-bold text-indigo-600">{arm.ucb_score.toFixed(3)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[11px]">Total Pulls:</span>
                      <span className="font-medium text-slate-700">{arm.pulls}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">Unit Cost: ₹{arm.base_cost.toFixed(2)}</span>
                  <span
                    className={`font-bold px-2 py-0.5 rounded-full text-[10px] ${
                      arm.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {arm.is_active ? 'ACTIVE' : 'KILLED'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  )
}

