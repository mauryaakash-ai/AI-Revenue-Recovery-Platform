import React from 'react'
import { X, ShieldCheck, CheckCircle2, AlertTriangle, ArrowRight, Layers, HelpCircle, FileText, Lock } from 'lucide-react'

interface DecisionCardModalProps {
  isOpen: boolean
  onClose: () => void
  decisionCard: any
  onApprove?: () => void
}

export const DecisionCardModal: React.FC<DecisionCardModalProps> = ({
  isOpen,
  onClose,
  decisionCard,
  onApprove
}) => {
  if (!isOpen || !decisionCard) return null

  const rec = decisionCard.recommendation || {}
  const fin = rec.financials || {}
  const gov = decisionCard.governance || {}

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-900">Next-Best-Action Decision Card</h3>
                <span className="font-mono text-[11px] text-slate-500">{decisionCard.decision_card_id}</span>
              </div>
              <p className="text-xs text-slate-500">Autonomous Policy & Causal Net Value Optimization</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 text-xs">
          {/* Primary Recommendation Banner */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50/40 border border-blue-200 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700">Primary Recommendation</span>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {Math.round(rec.recovery_probability * 100)}% Probability
              </span>
            </div>
            <p className="text-base font-bold text-slate-900 mt-1">{rec.primary_action}</p>
            <p className="text-xs text-slate-600 mt-0.5">
              Scheduled Window: <span className="font-semibold text-slate-800">{rec.scheduled_window}</span> ({rec.wait_delay_minutes}m Cooldown)
            </p>

            {/* Financial Formula Breakdown */}
            <div className="mt-3 grid grid-cols-3 gap-2 bg-white/90 border border-blue-100 rounded-lg p-2.5">
              <div>
                <p className="text-[10px] text-slate-400 font-semibold uppercase">Gross Expected</p>
                <p className="font-bold text-slate-900">₹{fin.gross_expected?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 font-semibold uppercase">Channel & Churn Cost</p>
                <p className="font-bold text-slate-700">₹{((fin.channel_cost || 0) + (fin.expected_churn_cost || 0))?.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-[10px] text-slate-400 font-semibold uppercase">Expected Net Value (ENRV)</p>
                <p className="font-bold text-emerald-700">₹{fin.expected_net_recovered_value?.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Alternatives Considered */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              Alternatives Considered & Rejected
            </h4>
            <div className="space-y-2">
              {decisionCard.alternatives_considered?.map((alt: any, idx: number) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800">{alt.action}</span>
                    <span className="text-slate-500 font-mono">{Math.round(alt.recovery_probability * 100)}% Prob</span>
                  </div>
                  <p className="text-[11px] text-rose-700 mt-0.5">Rejected: {alt.rejection_reason}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Feature Attributions */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
              Explainability & Feature Attributions
            </h4>
            <div className="space-y-1.5">
              {decisionCard.explainability_feature_attribution?.map((feat: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
                  <span className="text-slate-700">{feat.feature}</span>
                  <span className="font-mono text-[11px] font-bold text-blue-600">{Math.round(feat.weight * 100)}% Weight</span>
                </div>
              ))}
            </div>
          </div>

          {/* Counterfactual Analysis */}
          <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-3 text-amber-900">
            <span className="font-bold text-[11px] uppercase tracking-wider block mb-0.5">Counterfactual Analysis</span>
            <p className="text-xs leading-relaxed">{decisionCard.counterfactual_analysis}</p>
          </div>

          {/* Governance Pre-checks */}
          <div className="border-t border-slate-100 pt-3 flex items-center justify-between text-slate-600">
            <div>
              <p className="font-semibold text-slate-800">Policy Clearance: {gov.policy_checks_passed?.join(' · ')}</p>
              <p className="text-[11px] text-slate-400">{gov.approval_reason}</p>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase bg-blue-50 text-blue-700">
              Role: {gov.assigned_role}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-end gap-2.5">
          <button onClick={onClose} className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 text-xs font-semibold">
            Close
          </button>
          {onApprove && (
            <button
              onClick={() => {
                onApprove()
                onClose()
              }}
              className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              Approve & Execute Decision Card
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
