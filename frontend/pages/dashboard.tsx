import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface KPI {
  label: string
  value: string
  delta?: string
  trend?: 'up' | 'down' | 'neutral'
}

interface RevenueLeak {
  id: string
  type: string
  amount: number
  expected_recovery: number
  recovery_probability: number
  priority?: number
}

interface RecommendedAction {
  id: string
  type: string
  target_count?: number
  potential_recovery?: number
  confidence?: number
  risk_level?: string
}

export default function Dashboard() {
  const [merchantId, setMerchantId] = useState<string>('demo-merchant')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [kpis, setKpis] = useState<KPI[]>([])
  const [topLeaks, setTopLeaks] = useState<RevenueLeak[]>([])
  const [recommendedActions, setRecommendedActions] = useState<RecommendedAction[]>([])
  
  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true)
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        
        // Load revenue data
        const revenueRes = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/revenue?days=7`)
        const revenue = revenueRes.data
        
        // Load success rate
        const successRes = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/success-rate?days=7`)
        const success = successRes.data
        
        // Load revenue at risk
        const atRiskRes = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/revenue-at-risk?days=7`)
        const atRisk = atRiskRes.data
        
        // Load top leaks
        const leaksRes = await axios.get(`${baseUrl}/api/v1/merchants/${merchantId}/analytics/top-leaks?limit=5`)
        const leaks = leaksRes.data
        
        // Build KPIs
        const newKpis: KPI[] = [
          {
            label: 'Revenue Today',
            value: `₹${(revenue.today_revenue / 100000).toFixed(2)}L`,
            delta: `${revenue.delta_percentage >= 0 ? '+' : ''}${revenue.delta_percentage.toFixed(1)}%`,
            trend: revenue.delta_percentage >= 0 ? 'up' : 'down'
          },
          {
            label: 'Success Rate',
            value: `${success.success_rate.toFixed(1)}%`,
            trend: success.success_rate >= 90 ? 'up' : 'neutral'
          },
          {
            label: 'Revenue at Risk',
            value: `₹${(atRisk.total_at_risk / 100000).toFixed(2)}L`,
            trend: 'neutral'
          },
          {
            label: 'Potential Recovery',
            value: `₹${(atRisk.total_at_risk * 0.4 / 100000).toFixed(2)}L`,
            trend: 'up'
          }
        ]
        
        setKpis(newKpis)
        setTopLeaks(leaks.top_leaks || [])
        
        // Generate mock recommended actions
        setRecommendedActions([
          {
            id: '1',
            type: 'recovery_campaign',
            target_count: 10,
            potential_recovery: atRisk.total_at_risk * 0.3,
            confidence: 0.8,
            risk_level: 'low'
          }
        ])
        
        setError(null)
      } catch (err: any) {
        setError(`Failed to load dashboard: ${err.message}`)
      } finally {
        setLoading(false)
      }
    }
    
    loadDashboard()
  }, [merchantId])
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">RevPilot Dashboard</h1>
          <p className="text-gray-600">Revenue Intelligence & Recovery</p>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {kpis.map((kpi, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm font-medium">{kpi.label}</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{kpi.value}</p>
              {kpi.delta && (
                <p className={`text-sm mt-2 ${kpi.trend === 'up' ? 'text-green-600' : kpi.trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                  {kpi.trend === 'up' ? '↑' : kpi.trend === 'down' ? '↓' : '→'} {kpi.delta}
                </p>
              )}
            </div>
          ))}
        </div>
        
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Top Revenue Leaks */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Top Revenue Leaks</h2>
              
              {loading ? (
                <div className="text-gray-500">Loading...</div>
              ) : error ? (
                <div className="text-red-600 text-sm">{error}</div>
              ) : topLeaks.length === 0 ? (
                <div className="text-gray-500">No leaks detected - great job!</div>
              ) : (
                <div className="space-y-3">
                  {topLeaks.map((leak, idx) => (
                    <div key={leak.id} className="border border-gray-200 rounded p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            <span className="inline-block px-2 py-1 rounded text-xs font-semibold mr-2" 
                                  style={{backgroundColor: leak.type === 'failed_transaction' ? '#fee2e2' : '#fef3c7'}}>
                              {leak.type === 'failed_transaction' ? '❌ Failed' : '🔄 Refund'}
                            </span>
                            ₹{(leak.amount / 1000).toFixed(0)}k
                          </p>
                          <p className="text-xs text-gray-500 mt-1">Recovery: ₹{(leak.expected_recovery / 1000).toFixed(0)}k ({(leak.recovery_probability * 100).toFixed(0)}%)</p>
                        </div>
                        <div className="text-right">
                          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                            <span className="text-white font-bold text-sm">{((idx + 1) * 10)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          {/* Recommended Actions */}
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Recommended Actions</h2>
              
              <div className="space-y-3">
                {recommendedActions.map((action) => (
                  <div key={action.id} className="border border-gray-200 rounded p-4 hover:bg-blue-50">
                    <p className="text-sm font-medium text-gray-900">Recovery Campaign</p>
                    <p className="text-xs text-gray-600 mt-1">Target: {action.target_count} customers</p>
                    <p className="text-xs text-gray-600">Recovery: ₹{((action.potential_recovery || 0) / 100000).toFixed(1)}L</p>
                    <p className="text-xs text-gray-600">Confidence: {((action.confidence || 0) * 100).toFixed(0)}%</p>
                    <button className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-2 px-3 rounded transition">
                      Review & Approve
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Ask RevPilot */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Ask RevPilot</h2>
          <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Why is revenue down today?" 
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition">
              Investigate
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
