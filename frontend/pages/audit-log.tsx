import React, { useEffect, useState } from 'react'
import axios from 'axios'

interface AuditEntry {
  id: string
  action: string
  tool?: string
  status: string
  approval_status?: string
  timestamp: string
  result: string
}

export default function AuditLog() {
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [merchantId] = useState('demo-merchant')
  const [filter, setFilter] = useState<'all' | 'approved' | 'rejected' | 'pending'>('all')
  
  useEffect(() => {
    const loadAuditLog = async () => {
      try {
        setLoading(true)
        // Mock audit entries for now
        const mockEntries: AuditEntry[] = [
          {
            id: '1',
            action: 'detect_anomalies',
            tool: 'analytics',
            status: 'executed',
            approval_status: 'auto_approved',
            timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
            result: 'success'
          },
          {
            id: '2',
            action: 'get_revenue',
            tool: 'analytics',
            status: 'executed',
            approval_status: 'auto_approved',
            timestamp: new Date(Date.now() - 10 * 60000).toISOString(),
            result: 'success'
          },
          {
            id: '3',
            action: 'create_payment_link',
            tool: 'actions',
            status: 'executed',
            approval_status: 'auto_approved',
            timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
            result: 'success'
          },
          {
            id: '4',
            action: 'refund_payment',
            tool: 'actions',
            status: 'pending',
            approval_status: 'pending',
            timestamp: new Date(Date.now() - 20 * 60000).toISOString(),
            result: 'pending'
          }
        ]
        
        setEntries(mockEntries)
      } catch (error) {
        console.error('Failed to load audit log:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadAuditLog()
  }, [merchantId])
  
  const filtered = entries.filter(entry => {
    if (filter === 'all') return true
    return entry.approval_status === filter || entry.status === filter
  })
  
  const getActionBadge = (action: string) => {
    if (action.includes('detect') || action.includes('get')) return 'info'
    if (action.includes('create') || action.includes('send')) return 'action'
    if (action.includes('refund') || action.includes('payout')) return 'sensitive'
    return 'default'
  }
  
  const getBadgeColors = (type: string) => {
    switch (type) {
      case 'info':
        return 'bg-blue-100 text-blue-800'
      case 'action':
        return 'bg-green-100 text-green-800'
      case 'sensitive':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
          <p className="text-gray-600">All agent actions and approvals</p>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="mb-6 flex gap-2">
          {(['all', 'approved', 'rejected', 'pending'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-200 hover:border-gray-300'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        
        {/* Log Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-6 text-center text-gray-500">Loading...</div>
          ) : filtered.length === 0 ? (
            <div className="p-6 text-center text-gray-500">No entries found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Timestamp</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Action</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Tool</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Approval</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Result</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filtered.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(entry.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getBadgeColors(getActionBadge(entry.action))}`}>
                          {entry.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {entry.tool || '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                          entry.status === 'executed' ? 'bg-green-100 text-green-800' :
                          entry.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {entry.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                          entry.approval_status === 'auto_approved' ? 'bg-blue-100 text-blue-800' :
                          entry.approval_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {entry.approval_status || '—'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <span className={entry.result === 'success' ? 'text-green-600' : entry.result === 'pending' ? 'text-yellow-600' : 'text-red-600'}>
                          {entry.result === 'success' ? '✓' : entry.result === 'pending' ? '⏳' : '✗'} {entry.result}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
