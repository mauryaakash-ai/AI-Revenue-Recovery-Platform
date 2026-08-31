import React from 'react'

interface ProbabilityBadgeProps {
  probability: number // 0.0 to 1.0 or 0 to 100
  showBar?: boolean
}

export const ProbabilityBadge: React.FC<ProbabilityBadgeProps> = ({ probability, showBar = false }) => {
  const pct = probability <= 1.0 ? Math.round(probability * 100) : Math.round(probability)
  
  let colorClass = 'text-emerald-700 bg-emerald-50 border-emerald-200'
  let barColor = 'bg-emerald-500'

  if (pct < 65) {
    colorClass = 'text-amber-700 bg-amber-50 border-amber-200'
    barColor = 'bg-amber-500'
  } else if (pct < 50) {
    colorClass = 'text-red-700 bg-red-50 border-red-200'
    barColor = 'bg-red-500'
  }

  return (
    <div className="inline-flex flex-col gap-1">
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${colorClass}`}>
        {pct}% Probability
      </span>
      {showBar && (
        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
          <div className={`h-full ${barColor} rounded-full`} style={{ width: `${pct}%` }} />
        </div>
      )}
    </div>
  )
}

