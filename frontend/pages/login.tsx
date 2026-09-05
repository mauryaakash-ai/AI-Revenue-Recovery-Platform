import React, { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { 
  Shield, CheckCircle2, Smartphone, Mail, Lock, ArrowRight, 
  Sparkles, KeyRound, PhoneCall, RefreshCw, AlertCircle, Building2, User
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const router = useRouter()
  const { login, loginWithOtp, sendOtp, switchPersona } = useAuth()

  const [activeTab, setActiveTab] = useState<'email' | 'otp'>('email')
  const [email, setEmail] = useState('akash@urbankart.com')
  const [password, setPassword] = useState('••••••••')
  const [phone, setPhone] = useState('+91 98201 94821')
  const [otp, setOtp] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [otpHint, setOtpHint] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const demoPersonas = [
    {
      id: 'usr_akash_01',
      name: 'Akash Sharma',
      role: 'Admin & Founder',
      company: 'UrbanKart E-Commerce',
      email: 'akash@urbankart.com',
      avatar: 'AK',
      badgeColor: 'bg-blue-100 text-blue-800'
    },
    {
      id: 'usr_neha_02',
      name: 'Neha Verma',
      role: 'Revenue Operations Lead',
      company: 'UrbanKart E-Commerce',
      email: 'neha@revpilot.ai',
      avatar: 'NV',
      badgeColor: 'bg-purple-100 text-purple-800'
    },
    {
      id: 'usr_vikram_03',
      name: 'Vikram Patel',
      role: 'Finance Director',
      company: 'CloudMart B2B',
      email: 'vikram@cfo-desk.in',
      avatar: 'VP',
      badgeColor: 'bg-emerald-100 text-emerald-800'
    },
    {
      id: 'usr_priya_04',
      name: 'Priya Nair',
      role: 'Compliance & Risk Officer',
      company: 'Nova Health',
      email: 'priya@fintech-guard.com',
      avatar: 'PN',
      badgeColor: 'bg-amber-100 text-amber-800'
    }
  ]

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const success = await login(email, password)
      if (success) {
        router.push('/')
      } else {
        setError('Invalid credentials. You can use any demo persona below.')
      }
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSendOtp = async () => {
    setError(null)
    setLoading(true)
    try {
      const res = await sendOtp(phone)
      if (res.success) {
        setOtpSent(true)
        setOtpHint(res.hint || '482910')
        if (res.hint) {
          setOtp(res.hint)
        }
      } else {
        setError('Failed to dispatch demo OTP')
      }
    } catch (err: any) {
      setError(err.message || 'OTP dispatch failed')
    } finally {
      setLoading(false)
    }
  }

  const handleOtpVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const success = await loginWithOtp(phone, otp)
      if (success) {
        router.push('/')
      } else {
        setError('Invalid OTP code. Try entering 482910.')
      }
    } catch (err: any) {
      setError(err.message || 'OTP verification failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPersona = async (persona: typeof demoPersonas[0]) => {
    setLoading(true)
    setError(null)
    try {
      await switchPersona(persona.id)
      router.push('/')
    } catch (err) {
      setError('Persona switch failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>Login | Razorpay AI Revenue Recovery Platform</title>
      </Head>

      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between font-sans selection:bg-blue-600 selection:text-white">
        {/* Subtle Background Glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl" />
          <div className="absolute top-1/3 -right-40 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-teal-600/15 rounded-full blur-3xl" />
        </div>

        {/* Top Header */}
        <header className="relative z-10 w-full max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-600/30">
              <span className="text-base tracking-tight">R</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white">Razorpay</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 uppercase tracking-wider">
                  AI RevPilot
                </span>
              </div>
              <p className="text-[11px] text-slate-400 -mt-0.5">Autonomous Revenue Recovery Platform</p>
            </div>
          </Link>

          <Link
            href="/"
            className="text-xs font-semibold text-slate-400 hover:text-white transition flex items-center gap-1.5"
          >
            <span>Bypass to Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </header>

        {/* Main Content */}
        <main className="relative z-10 w-full max-w-7xl mx-auto px-6 py-8 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Platform Showcase */}
          <div className="lg:col-span-6 space-y-8">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next-Gen Autonomous Fintech Intelligence</span>
              </div>
              
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
                Recover lost revenue with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-teal-400">AI-powered precision</span>.
              </h1>

              <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-xl">
                Real-time failed transaction forensics, zero-cost Hinglish voice calls, automated DLT SMS recovery, and proactive customer retention.
              </p>
            </div>

            {/* Benchmark Metrics Grid */}
            <div className="grid grid-cols-3 gap-3 max-w-lg">
              <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-4 shadow-xl backdrop-blur-xs">
                <p className="text-[11px] text-slate-400 font-medium">Recoverable Volume</p>
                <p className="text-xl font-bold text-white mt-1">₹1.14 Cr</p>
                <p className="text-[10px] text-blue-400 mt-0.5">62.6% addressable</p>
              </div>
              <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-4 shadow-xl backdrop-blur-xs">
                <p className="text-[11px] text-slate-400 font-medium">Recovery Rate</p>
                <p className="text-xl font-bold text-emerald-400 mt-1">68.9%</p>
                <p className="text-[10px] text-slate-400 mt-0.5">+14.9% vs benchmark</p>
              </div>
              <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-4 shadow-xl backdrop-blur-xs">
                <p className="text-[11px] text-slate-400 font-medium">Net Realized ROI</p>
                <p className="text-xl font-bold text-teal-400 mt-1">3,175%</p>
                <p className="text-[10px] text-teal-300 mt-0.5">₹76.2L recovered</p>
              </div>
            </div>

            {/* Capability Feature Bullets */}
            <div className="space-y-3 pt-2 text-xs text-slate-300 max-w-lg">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
                <span>Free In-Browser WebRTC VoIP & Hinglish AI Voice Agent</span>
              </div>
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>TRAI DLT-Compliant SMS Gateway with Real Free Delivery</span>
              </div>
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>Smart Multi-Agent Autonomous Retries with NPCI Quiet Hours</span>
              </div>
            </div>
          </div>

          {/* Right Column: Modern Authentication Card */}
          <div className="lg:col-span-6 w-full max-w-md mx-auto">
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 backdrop-blur-md space-y-6">
              {/* Card Header */}
              <div>
                <h2 className="text-xl font-bold text-white tracking-tight">Sign in to RevPilot</h2>
                <p className="text-xs text-slate-400 mt-1">Access your autonomous recovery control center.</p>
              </div>

              {/* Login Method Tab Switcher */}
              <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800">
                <button
                  type="button"
                  onClick={() => { setActiveTab('email'); setError(null); }}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-lg transition ${
                    activeTab === 'email' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Mail className="w-3.5 h-3.5" />
                  <span>Email & Personas</span>
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab('otp'); setError(null); }}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-lg transition ${
                    activeTab === 'otp' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Smartphone className="w-3.5 h-3.5" />
                  <span>Phone SMS OTP</span>
                  <span className="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-400 text-[9px] rounded font-mono font-bold">FREE</span>
                </button>
              </div>

              {/* Error Banner */}
              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                  <span>{error}</span>
                </div>
              )}

              {/* TAB 1: EMAIL & PASSWORD */}
              {activeTab === 'email' && (
                <form onSubmit={handleEmailLogin} className="space-y-4 text-xs">
                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Corporate Email Address</label>
                    <div className="relative">
                      <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="akash@urbankart.com"
                        className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="text-slate-300 font-semibold">Password</label>
                      <span className="text-[10px] text-slate-500">Any password works for demo</span>
                    </div>
                    <div className="relative">
                      <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <ArrowRight className="w-4 h-4" />
                    {loading ? 'Authenticating...' : 'Sign In with Email'}
                  </button>
                </form>
              )}

              {/* TAB 2: FREE DEMO SMS OTP */}
              {activeTab === 'otp' && (
                <div className="space-y-4 text-xs">
                  <div>
                    <label className="block text-slate-300 font-semibold mb-1">Mobile Phone (+91)</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Smartphone className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input
                          type="tel"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="+91 98201 94821"
                          className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
                          required
                        />
                      </div>
                      <button
                        type="button"
                        onClick={handleSendOtp}
                        disabled={loading}
                        className="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl transition border border-slate-700 shrink-0 disabled:opacity-50"
                      >
                        {otpSent ? 'Resend OTP' : 'Send Free SMS OTP'}
                      </button>
                    </div>
                  </div>

                  {otpSent && (
                    <form onSubmit={handleOtpVerify} className="space-y-3 animate-in fade-in">
                      <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 space-y-1">
                        <div className="flex items-center justify-between font-semibold">
                          <span>Demo SMS OTP Dispatched!</span>
                          <span className="font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30 text-emerald-300">
                            {otpHint}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Dispatched via Demo SMS API to {phone}. Auto-filled for instant testing.
                        </p>
                      </div>

                      <div>
                        <label className="block text-slate-300 font-semibold mb-1">Enter 6-Digit OTP</label>
                        <div className="relative">
                          <KeyRound className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                          <input
                            type="text"
                            maxLength={6}
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            placeholder="482910"
                            className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono tracking-widest text-center text-sm placeholder:text-slate-600 focus:outline-none focus:border-blue-500"
                            required
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl transition shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        {loading ? 'Verifying OTP...' : 'Verify OTP & Launch Dashboard'}
                      </button>
                    </form>
                  )}
                </div>
              )}

              {/* ONE-CLICK DEMO PERSONAS */}
              <div className="pt-2 border-t border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Instant 1-Click Demo Personas
                  </span>
                  <span className="text-[10px] text-blue-400 font-medium">Click any persona to log in</span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {demoPersonas.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => handleSelectPersona(p)}
                      disabled={loading}
                      className="p-2.5 bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 rounded-xl text-left transition group disabled:opacity-50"
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-200 flex items-center justify-center font-bold text-xs group-hover:bg-blue-600 group-hover:text-white transition">
                          {p.avatar}
                        </div>
                        <div className="truncate">
                          <p className="text-xs font-semibold text-white truncate">{p.name}</p>
                          <p className="text-[10px] text-slate-400 truncate">{p.role}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Guest Explore Action */}
              <div className="text-center pt-2">
                <Link
                  href="/"
                  className="text-xs text-slate-400 hover:text-white underline transition"
                >
                  Continue as Guest Explorer →
                </Link>
              </div>
            </div>
          </div>
        </main>

        {/* Footer Regulatory Seals */}
        <footer className="relative z-10 border-t border-slate-900 bg-slate-950/80 py-4 px-6 text-center text-[11px] text-slate-500">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <Shield className="w-3.5 h-3.5 text-blue-500" />
                RBI Licensed Payment Aggregator Standard
              </span>
              <span>•</span>
              <span>256-Bit TLS End-to-End Encryption</span>
            </div>
            <span>© 2026 Razorpay RevPilot AI. All rights reserved.</span>
          </div>
        </footer>
      </div>
    </>
  )
}

