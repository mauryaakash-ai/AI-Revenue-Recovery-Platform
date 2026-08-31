import React from 'react'
import { X, CheckCircle2, ShieldCheck, Sparkles, HelpCircle } from 'lucide-react'

interface ExplainabilityModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  recommendation?: string
  expectedUplift?: string
  reasons: string[]
  onApprove?: () => void
}

export const ExplainabilityModal: React.FC<ExplainabilityModalProps> = ({
  isOpen,
  onClose,
  title = 'AI Recommendation Explainability',
  recommendation = 'Prioritize UPI retries between 7:30 PM and 9:00 PM',
  expectedUplift = '₹7.2L – ₹8.1L',
  reasons = [],
  onApprove
}) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
              <p className="text-xs text-slate-500">Deterministic Model Rationale & Feature Attribution</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-100 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-blue-50/50 border border-blue-100 rounded-lg p-3.5">
            <p className="text-xs font-semibold text-blue-900">Recommended Action:</p>
            <p className="text-sm font-medium text-blue-700 mt-0.5">{recommendation}</p>
            {expectedUplift && (
              <p className="text-xs text-blue-600 mt-1">Expected incremental recovery: <span className="font-semibold">{expectedUplift}</span></p>
            )}
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
              Why this recommendation?
            </h4>
            <div className="space-y-2">
              {reasons.map((reason, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 border border-slate-100">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <p className="text-xs text-slate-700 leading-relaxed">{reason}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded border border-slate-100">
            <span className="font-medium text-slate-700">Governance Note:</span> All AI actions require human approval by default according to Razorpay merchant policy. Auto-execution can be configured in Settings.
          </div>
        </div>

        <div className="flex items-center justify-end gap-2.5 px-6 py-3.5 border-t border-slate-100 bg-slate-50/50">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-md text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 transition"
          >
            Close
          </button>
          {onApprove && (
            <button
              onClick={() => {
                onApprove()
                onClose()
              }}
              className="px-4 py-1.5 rounded-md text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 transition flex items-center gap-1.5"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              Approve Recommendation
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

