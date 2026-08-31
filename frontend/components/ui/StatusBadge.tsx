import React from 'react'

interface StatusBadgeProps {
  status: string
  type?: 'priority' | 'status' | 'method' | 'severity'
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'status' }) => {
  const normalized = status.toLowerCase()

  // Priority Styles
  if (type === 'priority') {
    switch (normalized) {
      case 'critical':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-700 border border-red-200">Critical</span>
      case 'high':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">High Priority</span>
      case 'medium':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">Medium</span>
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">Low</span>
    }
  }

  // Severity Styles
  if (type === 'severity') {
    switch (normalized) {
      case 'critical':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800">Critical Severity</span>
      case 'high':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800">High Severity</span>
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">Operational Alert</span>
    }
  }

  // General Status Styles
  switch (normalized) {
    case 'recovered':
    case 'success':
    case 'completed':
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">Recovered</span>
    case 'scheduled':
    case 'in_progress':
    case 'pending':
    case 'identified':
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">Active Queue</span>
    case 'failed':
    case 'abandoned':
    case 'dismissed':
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">Failed</span>
    default:
      return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">{status}</span>
  }
}

