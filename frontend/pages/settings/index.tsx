import React, { useState } from 'react'
import {
  Shield, Key, UserCheck, Bell, Sliders, CheckCircle2, Lock, Save
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

export default function SettingsPage() {
  const [merchantId, setMerchantId] = useState('merchant_urbankart')
  const [autoThreshold, setAutoThreshold] = useState(85)
  const [cooldownMinutes, setCooldownMinutes] = useState(90)
  const [autoExecute, setAutoExecute] = useState(false)
  const [saved, setSaved] = useState(false)

  const roles = [
    { name: 'Admin', desc: 'Full administrative access and policy provisioning', permissions: ['Configure AI Policy', 'Batch Approve', 'Edit Strategies', 'Export Financials', 'Manage Users'] },
    { name: 'Revenue Operations', desc: 'Daily execution of recovery queues, experiments, and triage', permissions: ['Approve Recoveries', 'Edit Strategies', 'Launch Experiments', 'Export Data'] },
    { name: 'Finance', desc: 'Read-only financial telemetry, reconciliation, and audit logs', permissions: ['View Analytics', 'Export Ledgers', 'View Audit Logs'] },
    { name: 'Operations', desc: 'Manual review and recovery queue execution', permissions: ['Approve Recoveries', 'View Active Queue'] },
    { name: 'Analyst', desc: 'Intelligence exploration and experimentation analysis', permissions: ['View Analytics', 'View Forecast', 'View Experiments'] },
    { name: 'Support', desc: 'Customer lookup, timeline investigation, and support ticket triage', permissions: ['View Transactions', 'View Customer Profile'] },
  ]

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <AppShell merchantId={merchantId} onMerchantChange={setMerchantId}>
      <div className="pb-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Platform Settings & Governance</h1>
        <p className="text-xs text-slate-500 mt-1">
          Configure autonomous recovery parameters, security policies, and role-based operational permissions.
        </p>
      </div>

      <div className="mt-6 space-y-8">
        {/* Autonomous Execution Policy */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center gap-2.5 mb-4">
            <Sliders className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Autonomous AI Execution Policy</h3>
          </div>

          <form onSubmit={handleSave} className="space-y-4 max-w-xl text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
              <div>
                <p className="font-bold text-slate-900">Require Human Approval for Recoveries</p>
                <p className="text-slate-500 text-[11px]">When enabled, AI recommendations must be approved before triggering payment requests.</p>
              </div>
              <input
                type="checkbox"
                checked={!autoExecute}
                onChange={(e) => setAutoExecute(!e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>Autonomous Execution Probability Threshold</span>
                <span className="font-mono text-blue-600">{autoThreshold}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                value={autoThreshold}
                onChange={(e) => setAutoThreshold(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">Only recovery candidates with &gt; {autoThreshold}% ML confidence will qualify for zero-touch retry.</p>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Default Cooldown Delay Between Retries (Minutes)</label>
              <input
                type="number"
                value={cooldownMinutes}
                onChange={(e) => setCooldownMinutes(Number(e.target.value))}
                className="w-full p-2 border border-slate-200 rounded-lg focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-xs transition flex items-center gap-1.5"
              >
                <Save className="w-3.5 h-3.5" />
                Save Policy Configurations
              </button>
              {saved && <span className="text-emerald-600 font-semibold text-xs ml-3">Settings saved successfully!</span>}
            </div>
          </form>
        </div>

        {/* Section 35: Role-Based Access Control Matrix */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="flex items-center gap-2.5 mb-4">
            <UserCheck className="w-5 h-5 text-blue-600" />
            <div>
              <h3 className="text-base font-bold text-slate-900">Role-Based Access Control (RBAC)</h3>
              <p className="text-xs text-slate-500">Separation of duties and granular permissions across Razorpay merchant team roles.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {roles.map((r, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">{r.name}</span>
                    <Lock className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">{r.desc}</p>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-200/60 space-y-1">
                  {r.permissions.map((p, pIdx) => (
                    <div key={pIdx} className="flex items-center gap-1.5 text-[11px] text-slate-700">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                      <span>{p}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  )
}

