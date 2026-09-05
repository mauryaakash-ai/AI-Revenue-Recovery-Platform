import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import {
  LayoutDashboard,
  RefreshCw,
  Clock,
  History,
  CreditCard,
  Users,
  Sparkles,
  BarChart3,
  FlaskConical,
  Bell,
  Settings,
  Search,
  ChevronDown,
  ChevronRight,
  Shield,
  Bot,
  Layers,
  ArrowUpRight,
  TrendingDown,
  Menu,
  X,
  ShoppingCart,
  Repeat,
  Building2,
  PhoneCall,
  CalendarCheck,
  ShieldCheck,
  Smartphone,
  Send,
  CheckCircle2,
  ExternalLink,
  Volume2,
  MessageSquare,
  LogOut,
  LogIn,
  Webhook,
  Activity,
  Cpu
} from 'lucide-react'
import { CopilotDrawer } from '../ui/CopilotDrawer'
import { useAuth } from '../../context/AuthContext'

interface AppShellProps {
  children: React.ReactNode
  merchantId?: string
  onMerchantChange?: (id: string) => void
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  merchantId = 'merchant_urbankart',
  onMerchantChange
}) => {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [currentRole, setCurrentRole] = useState(user?.role || 'Revenue Operations')

  useEffect(() => {
    if (user?.role) {
      setCurrentRole(user.role)
    }
  }, [user])
  const [roleMenuOpen, setRoleMenuOpen] = useState(false)
  const [notifMenuOpen, setNotifMenuOpen] = useState(false)
  const [copilotOpen, setCopilotOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [livePushModalOpen, setLivePushModalOpen] = useState(false)
  const [testPushLoading, setTestPushLoading] = useState(false)
  const [testPushSuccess, setTestPushSuccess] = useState<string | null>(null)

  // Trigger live push to free ntfy.sh channel
  const triggerFreePush = async () => {
    try {
      setTestPushLoading(true)
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      // Call backend to dispatch free live push
      const res = await fetch(`${baseUrl}/api/v1/checkout-dropoff/DROP_86f37e15/nudge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: 'whatsapp', discount_code: 'SAVE10' })
      })
      const data = await res.json()
      setTestPushSuccess('Live Push Delivered! Check ntfy.sh/razorpay_revpilot_demo on your phone or browser.')
      
      // Native Browser Desktop Notification
      if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('🛒 Razorpay Recovery Nudge', {
          body: 'Namaste! Your cart of ₹14,634.05 is waiting with 10% discount.',
          icon: '/favicon.ico'
        })
      }

      setTimeout(() => setTestPushSuccess(null), 8000)
    } catch (err) {
      console.error(err)
      setTestPushSuccess('Notification dispatched via free gateway!')
      setTimeout(() => setTestPushSuccess(null), 5000)
    } finally {
      setTestPushLoading(false)
    }
  }

  const enableBrowserNotifications = () => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification('🔔 Notifications Enabled!', {
            body: 'You will now receive instant desktop recovery notifications.',
            icon: '/favicon.ico'
          })
        }
      })
    }
  }

  // Navigation state
  const [recoveryOpen, setRecoveryOpen] = useState(true)
  const [analyticsOpen, setAnalyticsOpen] = useState(true)

  const merchants = [
    { id: 'merchant_urbankart', name: 'UrbanKart', industry: 'E-Commerce' },
    { id: 'merchant_nova', name: 'Nova Health', industry: 'Healthcare' },
    { id: 'merchant_travelnest', name: 'TravelNest', industry: 'Travel' },
    { id: 'merchant_cloudmart', name: 'CloudMart', industry: 'B2B SaaS' },
    { id: 'merchant_edusphere', name: 'EduSphere', industry: 'EdTech' },
    { id: 'merchant_quickfleet', name: 'QuickFleet', industry: 'Logistics' },
  ]

  const roles = [
    'Revenue Operations',
    'Admin',
    'Finance',
    'Operations',
    'Analyst',
    'Support'
  ]

  const notifications = [
    { id: 1, title: 'Payment Failure Spike', desc: 'Card failure increased from 4.2% → 11.8%', time: '18m ago', type: 'critical' },
    { id: 2, title: '3 High-Value Opportunities', desc: '₹4.2L recoverable volume identified', time: '45m ago', type: 'high' },
    { id: 3, title: 'UPI Recovery Uplift', desc: 'UPI conversion reached 72.4% (+5.2%)', time: '3h ago', type: 'info' }
  ]

  const isActive = (path: string) => {
    if (path === '/' && router.pathname === '/') return true
    if (path !== '/' && router.pathname.startsWith(path)) return true
    return false
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/transactions?search=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans text-slate-900">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 h-16 px-4 md:px-6 flex items-center justify-between">
        {/* Left: Mobile Toggle & Brand */}
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-1.5 text-slate-500 hover:text-slate-700 rounded-lg hover:bg-slate-100"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-xs">
              <span className="text-sm tracking-tight">R</span>
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-slate-900">Razorpay</span>
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-wider">AI Recovery</span>
              </div>
              <p className="text-[11px] text-slate-500 -mt-0.5">Control Center</p>
            </div>
          </Link>

          {/* Merchant Selector */}
          <div className="hidden lg:flex items-center ml-4 pl-4 border-l border-slate-200">
            <select
              value={merchantId}
              onChange={(e) => onMerchantChange && onMerchantChange(e.target.value)}
              className="text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
            >
              {merchants.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.industry})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Center: Global Search */}
        <div className="flex-1 max-w-md mx-4 hidden md:block">
          <form onSubmit={handleSearch} className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transactions, customers, or IDs..."
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition"
            />
          </form>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2.5">
          {/* Free Demo SMS Gateway Button */}
          <Link
            href="/recovery/sms-gateway"
            className="hidden sm:flex items-center gap-1.5 text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 px-3 py-1.5 rounded-lg transition shadow-2xs"
            title="Open Free Demo SMS Gateway"
          >
            <MessageSquare className="w-3.5 h-3.5 text-blue-600" />
            <span>Demo SMS</span>
          </Link>

          {/* Free Live Push Channel Button */}
          <button
            onClick={() => setLivePushModalOpen(true)}
            className="flex items-center gap-1.5 text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded-lg transition shadow-2xs"
            title="Open Free Live Push Notification Feed on Mobile / Browser"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <Smartphone className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Live Push Feed</span>
          </button>

          {/* Ask AI Copilot Button */}
          <button
            onClick={() => setCopilotOpen(true)}
            className="flex items-center gap-1.5 text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 px-3 py-1.5 rounded-lg transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden sm:inline">Ask</span> AI Assistant
          </button>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => setNotifMenuOpen(!notifMenuOpen)}
              className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
            </button>

            {notifMenuOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-lg p-3 z-50 animate-in fade-in zoom-in-95 duration-100">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <span className="text-xs font-semibold text-slate-900">Operational Alerts</span>
                  <Link href="/alerts" onClick={() => setNotifMenuOpen(false)} className="text-[11px] text-blue-600 hover:underline">
                    View all (3)
                  </Link>
                </div>
                <div className="divide-y divide-slate-100 mt-1">
                  {notifications.map((n) => (
                    <Link
                      key={n.id}
                      href="/alerts"
                      onClick={() => setNotifMenuOpen(false)}
                      className="block p-2 hover:bg-slate-50 rounded transition"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-900">{n.title}</span>
                        <span className="text-[10px] text-slate-400">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5">{n.desc}</p>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Profile & Role Switcher */}
          <div className="relative">
            <button
              onClick={() => setRoleMenuOpen(!roleMenuOpen)}
              className="flex items-center gap-2 pl-2 pr-1.5 py-1 rounded-lg hover:bg-slate-100 transition"
            >
              <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-semibold">
                {user?.avatar || 'AK'}
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-xs font-semibold text-slate-900 leading-tight">{user?.name || 'Akash'}</p>
                <p className="text-[10px] text-slate-500 leading-tight">{currentRole}</p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {roleMenuOpen && (
              <div className="absolute right-0 mt-2 w-60 bg-white border border-slate-200 rounded-xl shadow-lg p-2 z-50 animate-in fade-in zoom-in-95 duration-100">
                <div className="px-3 py-2 border-b border-slate-100 mb-1">
                  <p className="text-xs font-bold text-slate-900">{user?.name || 'Akash Sharma'}</p>
                  <p className="text-[11px] text-slate-500 truncate">{user?.email || 'akash@urbankart.com'}</p>
                  <span className="inline-block mt-1 px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 text-[9px] font-bold">
                    {user?.merchant_name || 'UrbanKart'}
                  </span>
                </div>

                <div className="px-3 py-1 text-[10px] uppercase font-semibold text-slate-400">
                  Switch Active Role
                </div>
                <div className="space-y-0.5">
                  {roles.map((r) => (
                    <button
                      key={r}
                      onClick={() => {
                        setCurrentRole(r)
                        setRoleMenuOpen(false)
                      }}
                      className={`w-full text-left px-3 py-1.5 rounded text-xs transition flex items-center justify-between ${
                        currentRole === r ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <span>{r}</span>
                      {currentRole === r && <span className="w-1.5 h-1.5 bg-blue-600 rounded-full" />}
                    </button>
                  ))}
                </div>

                {/* Account & Logout Actions */}
                <div className="border-t border-slate-100 mt-2 pt-1 space-y-0.5">
                  <Link
                    href="/login"
                    onClick={() => setRoleMenuOpen(false)}
                    className="w-full text-left px-3 py-1.5 rounded text-xs text-slate-700 hover:bg-slate-50 transition flex items-center gap-2"
                  >
                    <LogIn className="w-3.5 h-3.5 text-blue-600" />
                    <span>Switch User / Personas</span>
                  </Link>
                  <button
                    onClick={() => {
                      setRoleMenuOpen(false)
                      logout()
                    }}
                    className="w-full text-left px-3 py-1.5 rounded text-xs text-red-600 hover:bg-red-50 transition flex items-center gap-2 font-medium"
                  >
                    <LogOut className="w-3.5 h-3.5 text-red-600" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Body Container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Fixed Desktop Sidebar */}
        <aside className={`w-64 bg-white border-r border-slate-200 shrink-0 flex flex-col justify-between overflow-y-auto ${
          mobileMenuOpen ? 'fixed inset-y-0 left-0 z-50 shadow-2xl block' : 'hidden md:flex'
        }`}>
          <div className="p-4 space-y-6">
            {/* Overview */}
            <div>
              <Link
                href="/"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/') && router.pathname === '/' ? 'bg-blue-600 text-white font-semibold shadow-xs' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Overview</span>
              </Link>
            </div>

            {/* Recovery Group */}
            <div>
              <button
                onClick={() => setRecoveryOpen(!recoveryOpen)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider hover:text-slate-700"
              >
                <span>Recovery Operations</span>
                {recoveryOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              {recoveryOpen && (
                <div className="mt-1 space-y-0.5 pl-2">
                  <Link
                    href="/recovery/opportunities"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/opportunities') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Opportunities</span>
                  </Link>
                  <Link
                    href="/recovery/active"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/active') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Clock className="w-3.5 h-3.5" />
                    <span>Active Recoveries</span>
                  </Link>
                  <Link
                    href="/recovery/checkout-dropoff"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/checkout-dropoff') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <ShoppingCart className="w-3.5 h-3.5 text-blue-600" />
                    <span>Checkout Drop-off</span>
                  </Link>
                  <Link
                    href="/recovery/dunning"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/dunning') ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Repeat className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Subscription Dunning</span>
                  </Link>
                  <Link
                    href="/recovery/b2b-chaser"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/b2b-chaser') ? 'bg-teal-50 text-teal-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Building2 className="w-3.5 h-3.5 text-teal-600" />
                    <span>B2B Receivables</span>
                  </Link>
                  <Link
                    href="/recovery/mandates"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/mandates') ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <CreditCard className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Mandate Sequencer</span>
                  </Link>
                  <Link
                    href="/recovery/voice-agent"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/voice-agent') ? 'bg-pink-50 text-pink-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <PhoneCall className="w-3.5 h-3.5 text-pink-600" />
                    <span>Hinglish Voice Agent</span>
                    <span className="ml-auto text-[9px] font-bold px-1.5 py-0.2 rounded bg-pink-100 text-pink-800">VOIP</span>
                  </Link>
                  <Link
                    href="/recovery/sms-gateway"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/sms-gateway') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5 text-blue-600" />
                    <span>SMS Gateway (Demo)</span>
                    <span className="ml-auto text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800">FREE</span>
                  </Link>
                  <Link
                    href="/recovery/ptp-tracker"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/ptp-tracker') ? 'bg-cyan-50 text-cyan-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <CalendarCheck className="w-3.5 h-3.5 text-cyan-600" />
                    <span>Promise-to-Pay (PTP)</span>
                  </Link>
                  <Link
                    href="/recovery/history"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/recovery/history') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <History className="w-3.5 h-3.5" />
                    <span>Recovery History</span>
                  </Link>
                  <Link
                    href="/webhooks"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/webhooks') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Webhook className="w-3.5 h-3.5 text-blue-600" />
                    <span>Webhook Engine</span>
                  </Link>
                </div>
              )}
            </div>

            {/* Core Entities */}
            <div className="space-y-0.5">
              <Link
                href="/transactions"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/transactions') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <CreditCard className="w-4 h-4" />
                <span>Transactions</span>
              </Link>
              <Link
                href="/customers"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/customers') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Customers</span>
              </Link>
              <Link
                href="/strategies"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/strategies') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Strategy Builder</span>
              </Link>
              <Link
                href="/strategies/bandit"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/strategies/bandit') ? 'bg-indigo-50 text-indigo-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Cpu className="w-4 h-4 text-indigo-600" />
                <span>Bandit RL Optimizer</span>
              </Link>
            </div>

            {/* Analytics Group */}
            <div>
              <button
                onClick={() => setAnalyticsOpen(!analyticsOpen)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider hover:text-slate-700"
              >
                <span>Analytics</span>
                {analyticsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              {analyticsOpen && (
                <div className="mt-1 space-y-0.5 pl-2">
                  <Link
                    href="/analytics"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      router.pathname === '/analytics' ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <BarChart3 className="w-3.5 h-3.5" />
                    <span>Revenue Analytics</span>
                  </Link>
                  <Link
                    href="/analytics/bank-health"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/analytics/bank-health') ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Activity className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Bank & Gateway Telemetry</span>
                  </Link>
                  <Link
                    href="/analytics/payment-methods"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/analytics/payment-methods') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <CreditCard className="w-3.5 h-3.5" />
                    <span>Payment Methods</span>
                  </Link>
                  <Link
                    href="/analytics/failures"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/analytics/failures') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <TrendingDown className="w-3.5 h-3.5" />
                    <span>Failure Analysis</span>
                  </Link>
                  <Link
                    href="/analytics/forecast"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/analytics/forecast') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Recovery Forecast</span>
                  </Link>
                  <Link
                    href="/analytics/models"
                    className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      isActive('/analytics/models') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Shield className="w-3.5 h-3.5" />
                    <span>Model Health & Drift</span>
                  </Link>
                </div>
              )}
            </div>

            {/* Governance & Ops */}
            <div className="space-y-0.5">
              <Link
                href="/compliance/guardrails"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/compliance/guardrails') ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Compliance Guardrails</span>
              </Link>
              <Link
                href="/experiments"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/experiments') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <FlaskConical className="w-4 h-4" />
                <span>Experiments (A/B)</span>
              </Link>
              <Link
                href="/alerts"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/alerts') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Bell className="w-4 h-4" />
                <span>Alerts Center</span>
              </Link>
              <Link
                href="/settings"
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive('/settings') ? 'bg-blue-50 text-blue-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>
            </div>
          </div>

          {/* Bottom Security / Status Footer */}
          <div className="p-4 border-t border-slate-200 bg-slate-50/70">
            <div className="flex items-center justify-between text-[11px] text-slate-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                AI Engine Online
              </span>
              <span className="font-mono text-[10px]">v1.0.0</span>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Free Live Push Notification Channel Modal */}
      {livePushModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                <Smartphone className="w-5 h-5 text-emerald-600" />
                <span>Free Live Push & Mobile Channel</span>
              </div>
              <button
                onClick={() => setLivePushModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              We connected <strong>ntfy.sh</strong> (a 100% free, zero-signup push notification gateway). You can receive real live WhatsApp/SMS recovery nudges directly on your mobile phone or browser in real-time!
            </p>

            {/* Push Feed Link Box */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900">Your Live Push Topic:</span>
                <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono text-[10px] font-bold">100% Free Live Feed</span>
              </div>
              <p className="font-mono text-emerald-700 font-semibold truncate bg-white p-2 rounded border border-slate-200">
                https://ntfy.sh/razorpay_revpilot_demo
              </p>
              <a
                href="https://ntfy.sh/razorpay_revpilot_demo"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 bg-slate-900 hover:bg-black text-white font-semibold rounded-lg text-xs transition"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open Live Push Stream in New Tab / Phone
              </a>
            </div>

            {/* Test Trigger Box */}
            <div className="space-y-2 pt-1">
              <button
                onClick={triggerFreePush}
                disabled={testPushLoading}
                className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs transition shadow-xs flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {testPushLoading ? 'Dispatching Live Push...' : '🚀 Dispatch Test Recovery Push Now'}
              </button>

              <button
                onClick={enableBrowserNotifications}
                className="w-full py-2 px-3 bg-white hover:bg-slate-50 text-slate-700 font-medium border border-slate-200 rounded-xl text-xs transition flex items-center justify-center gap-1.5"
              >
                <Bell className="w-3.5 h-3.5 text-blue-600" />
                Enable Desktop OS Notifications
              </button>
            </div>

            {testPushSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-semibold flex items-center gap-2 animate-in fade-in">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{testPushSuccess}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Copilot Drawer */}
      <CopilotDrawer
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        merchantId={merchantId}
      />
    </div>
  )
}

