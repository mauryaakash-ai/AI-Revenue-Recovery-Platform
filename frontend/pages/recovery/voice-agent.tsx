import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { 
  PhoneCall, PhoneOff, Mic, MicOff, Volume2, Play, Pause, CheckCircle2, 
  Sparkles, RefreshCw, MessageSquare, Clock, UserCheck, 
  ArrowRight, Shield, AlertCircle, Headphones, VolumeX, PhoneForwarded,
  Hash, CalendarCheck, Send, Smartphone, Download, Search, FileText,
  ChevronDown, ChevronUp, User, AlertTriangle, CheckCircle, Info
} from 'lucide-react'
import { AppShell } from '../../components/layout/AppShell'

interface PersonaInfo {
  id: string
  name: string
  gender: string
  title: string
  badge: string
  emoji: string
  audioSample: string
}

const PERSONAS: Record<string, PersonaInfo> = {
  priya: {
    id: 'priya',
    name: 'Priya',
    gender: 'Female',
    title: 'Priority Care Specialist',
    badge: 'Expressive Neural HD',
    emoji: '👩‍💼',
    audioSample: '/audio/voices/priya_payment_retry.mp3'
  },
  rahul: {
    id: 'rahul',
    name: 'Rahul',
    gender: 'Male',
    title: 'Enterprise Recovery Lead',
    badge: 'Warm Professional',
    emoji: '👨‍💼',
    audioSample: '/audio/voices/rahul_payment_retry.mp3'
  },
  swara: {
    id: 'swara',
    name: 'Swara',
    gender: 'Female',
    title: 'Bilingual Hinglish Specialist',
    badge: 'Natural Hinglish',
    emoji: '🇮🇳',
    audioSample: '/audio/voices/swara_payment_retry.mp3'
  },
  madhur: {
    id: 'madhur',
    name: 'Madhur',
    gender: 'Male',
    title: 'Support & Gateway Lead',
    badge: 'Reassuring Tone',
    emoji: '🎙️',
    audioSample: '/audio/voices/madhur_payment_retry.mp3'
  },
  kavya: {
    id: 'kavya',
    name: 'Kavya',
    gender: 'Female',
    title: 'Resolution Desk Specialist',
    badge: 'Melodious Clarity',
    emoji: '🌸',
    audioSample: '/audio/voices/kavya_payment_retry.mp3'
  }
}

export default function VoiceAgentPage() {
  const [data, setData] = useState<any>(null)
  const [queueData, setQueueData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [queueLoading, setQueueLoading] = useState(true)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speakerOn, setSpeakerOn] = useState(true)

  // Softphone & Call State
  const [callState, setCallState] = useState<'idle' | 'dialing' | 'ringing' | 'connected' | 'ended'>('idle')
  const [callDuration, setCallDuration] = useState(0)
  const [activeCallSid, setActiveCallSid] = useState<string | null>(null)
  const [activeCallDetails, setActiveCallDetails] = useState<any>(null)
  const [dtmfFeedback, setDtmfFeedback] = useState<string | null>(null)

  // Softphone Dialer Form State
  const [dialPhone, setDialPhone] = useState('+91 98469 13810')
  const [customerName, setCustomerName] = useState('Ananya Sharma')
  const [amount, setAmount] = useState('45000')
  const [scenario, setScenario] = useState('failed_call')
  const [voicePersona, setVoicePersona] = useState<string>('rahul')
  const [currentTxnId, setCurrentTxnId] = useState<string | null>(null)
  const [telephonyFilter, setTelephonyFilter] = useState(false)

  // Queue State
  const [queueFilter, setQueueFilter] = useState<'all' | 'failed' | 'pending' | 'recovered' | 'ptp'>('all')
  const [queueSearch, setQueueSearch] = useState('')

  // Call History State
  const [historyStatusFilter, setHistoryStatusFilter] = useState<string>('all')
  const [historyPersonaFilter, setHistoryPersonaFilter] = useState<string>('all')
  const [historySearch, setHistorySearch] = useState('')
  const [expandedCallId, setExpandedCallId] = useState<string | null>(null)
  const [playingRecordingSid, setPlayingRecordingSid] = useState<string | null>(null)
  const [lastSavedCallSid, setLastSavedCallSid] = useState<string | null>(null)
  const [isSavingRecording, setIsSavingRecording] = useState(false)

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const timerRef = useRef<any>(null)
  const stopRingRef = useRef<(() => void) | null>(null)
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const recordingPlayerRef = useRef<HTMLAudioElement | null>(null)
  const dialerCardRef = useRef<HTMLDivElement | null>(null)

  // Fetch Call History
  const fetchCalls = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (historyStatusFilter !== 'all') params.append('call_status', historyStatusFilter)
      if (historyPersonaFilter !== 'all') params.append('voice_persona', historyPersonaFilter)
      if (historySearch) params.append('search', historySearch)

      const res = await axios.get(`${baseUrl}/api/v1/voice/calls?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch voice calls', err)
    } finally {
      setLoading(false)
    }
  }

  // Fetch Outbound Calling Queue (Pending & Failed)
  const fetchQueue = async () => {
    try {
      setQueueLoading(true)
      const params = new URLSearchParams()
      if (queueFilter !== 'all') params.append('status_filter', queueFilter)
      if (queueSearch) params.append('search', queueSearch)

      const res = await axios.get(`${baseUrl}/api/v1/voice/calling-queue?${params.toString()}`)
      setQueueData(res.data)
    } catch (err) {
      console.error('Failed to fetch calling queue', err)
    } finally {
      setQueueLoading(false)
    }
  }

  useEffect(() => {
    fetchCalls()
  }, [historyStatusFilter, historyPersonaFilter, historySearch])

  useEffect(() => {
    fetchQueue()
  }, [queueFilter, queueSearch])

  // Call duration counter
  useEffect(() => {
    if (callState === 'connected') {
      timerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [callState])

  // ==========================================
  // 1. Dual-Frequency DTMF Tones (Web Audio API)
  // ==========================================
  const playDTMF = (digit: string) => {
    if (typeof window === 'undefined') return
    try {
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext
      if (!AudioContext) return
      const ctx = new AudioContext()
      
      const freqMap: Record<string, [number, number]> = {
        '1': [697, 1209], '2': [697, 1336], '3': [697, 1477],
        '4': [770, 1209], '5': [770, 1336], '6': [770, 1477],
        '7': [852, 1209], '8': [852, 1336], '9': [852, 1477],
        '*': [941, 1209], '0': [941, 1336], '#': [941, 1477],
      }
      const freqs = freqMap[digit] || [697, 1209]
      
      const osc1 = ctx.createOscillator()
      const osc2 = ctx.createOscillator()
      const gain = ctx.createGain()
      
      osc1.frequency.value = freqs[0]
      osc2.frequency.value = freqs[1]
      gain.gain.value = 0.12
      
      osc1.connect(gain)
      osc2.connect(gain)
      gain.connect(ctx.destination)
      
      osc1.start()
      osc2.start()
      setTimeout(() => {
        osc1.stop()
        osc2.stop()
        ctx.close()
      }, 140)
    } catch (e) {
      console.warn('AudioContext DTMF note', e)
    }
  }

  // ==========================================
  // 2. Indian Telecom Ringback Tone Cadence (400Hz + 450Hz)
  // ==========================================
  const playRingbackTone = () => {
    if (typeof window === 'undefined') return () => {}
    try {
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext
      if (!AudioContext) return () => {}
      const ctx = new AudioContext()
      let stopped = false

      const playBurst = () => {
        if (stopped) return
        const osc1 = ctx.createOscillator()
        const osc2 = ctx.createOscillator()
        const gain = ctx.createGain()
        osc1.frequency.value = 400
        osc2.frequency.value = 450
        gain.gain.value = 0.08
        osc1.connect(gain)
        osc2.connect(gain)
        gain.connect(ctx.destination)
        osc1.start()
        osc2.start()
        setTimeout(() => {
          try {
            osc1.stop()
            osc2.stop()
          } catch(e) {}
          if (!stopped) {
            setTimeout(playBurst, 1800)
          }
        }, 1100)
      }
      playBurst()
      return () => {
        stopped = true
        try { ctx.close() } catch(e) {}
      }
    } catch (e) {
      return () => {}
    }
  }

  // ==========================================
  // 3. Audio Stop Helpers
  // ==========================================
  const stopSpeaking = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause()
      audioPlayerRef.current.currentTime = 0
      audioPlayerRef.current = null
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close().catch(() => {})
      audioCtxRef.current = null
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    setIsSpeaking(false)
  }

  const stopCallRecording = () => {
    if (recordingPlayerRef.current) {
      recordingPlayerRef.current.pause()
      recordingPlayerRef.current.currentTime = 0
      recordingPlayerRef.current = null
    }
    setPlayingRecordingSid(null)
  }

  // ==========================================
  // 4. Play Realistic Neural Voice Speech
  // ==========================================
  const playRealisticVoice = (audioPath?: string, fallbackText?: string) => {
    stopSpeaking()
    if (!speakerOn) return

    if (audioPath) {
      try {
        const audio = new Audio(audioPath)
        audioPlayerRef.current = audio

        if (telephonyFilter && typeof window !== 'undefined') {
          const AudioContext = window.AudioContext || (window as any).webkitAudioContext
          if (AudioContext) {
            const ctx = new AudioContext()
            audioCtxRef.current = ctx
            const source = ctx.createMediaElementSource(audio)
            const filter = ctx.createBiquadFilter()
            filter.type = 'bandpass'
            filter.frequency.value = 1800
            filter.Q.value = 0.85
            source.connect(filter)
            filter.connect(ctx.destination)
          }
        }

        audio.onplay = () => setIsSpeaking(true)
        audio.onended = () => {
          setIsSpeaking(false)
          if (audioCtxRef.current) {
            audioCtxRef.current.close().catch(() => {})
            audioCtxRef.current = null
          }
          if (activeCallSid) {
            saveCallRecord(activeCallSid)
          }
        }
        audio.onerror = () => setIsSpeaking(false)

        audio.play().catch(e => {
          console.warn('Audio playback error', e)
        })
        return
      } catch (err) {
        console.warn('Audio playback catch', err)
      }
    }
  }

  // Audition / Preview a Persona's Voice
  const previewPersonaVoice = (personaKey: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const persona = PERSONAS[personaKey]
    if (!persona) return
    playRealisticVoice(persona.audioSample)
  }

  // Play Call Recording in History Table
  const togglePlayRecording = (recordingUrl: string, sid: string) => {
    if (playingRecordingSid === sid) {
      stopCallRecording()
      return
    }

    stopCallRecording()
    stopSpeaking()

    try {
      const resolvedUrl = recordingUrl?.startsWith('http') || recordingUrl?.startsWith('/') 
        ? recordingUrl 
        : `/${recordingUrl}`

      const audio = new Audio(resolvedUrl)
      recordingPlayerRef.current = audio
      setPlayingRecordingSid(sid)

      audio.onended = () => {
        setPlayingRecordingSid(null)
      }
      audio.onerror = (e) => {
        console.warn('Audio playback error', e)
        setPlayingRecordingSid(null)
      }

      audio.play().catch(e => {
        console.warn('Recording playback failed', e)
        setPlayingRecordingSid(null)
      })
    } catch (err) {
      console.warn('Audio play error', err)
      setPlayingRecordingSid(null)
    }
  }

  // ==========================================
  // Guaranteed Call Recording Persister
  // ==========================================
  const saveCallRecord = async (sid: string, statusOverride?: string) => {
    if (!sid) return
    try {
      setIsSavingRecording(true)
      const finalStatus = statusOverride || (
        dtmfFeedback?.includes('RECOVERED') ? 'recovered' : 
        dtmfFeedback?.includes('PTP') ? 'ptp_committed' : 
        'completed'
      )
      const finalDuration = Math.max(callDuration, 36)
      const recordingPath = activeCallDetails?.audio_url || `/audio/voices/${voicePersona}_${scenario}.mp3`

      const res = await axios.post(`${baseUrl}/api/v1/voice/call/save-recording`, {
        call_sid: sid,
        customer_name: customerName,
        customer_phone: dialPhone,
        amount: parseFloat(amount) || 14500,
        duration_seconds: finalDuration,
        call_status: finalStatus,
        voice_persona: voicePersona,
        scenario: scenario,
        transaction_id: currentTxnId,
        recording_url: recordingPath,
        transcript_hinglish: activeCallDetails?.transcript_hinglish,
        transcript_english: activeCallDetails?.transcript_english
      })

      setLastSavedCallSid(sid)
      const pName = PERSONAS[voicePersona]?.name || 'Agent'
      setActionSuccess(`🎙️ Call Recording Saved to Ledger! (SID: ${sid} · Duration: ${formatSeconds(finalDuration)} · Persona: ${pName} · Status: ${finalStatus.toUpperCase()})`)
      
      await fetchCalls()
      await fetchQueue()
      return res.data
    } catch (err) {
      console.error('Save recording error', err)
    } finally {
      setIsSavingRecording(false)
    }
  }

  // ==========================================
  // 5. Launch Outbound Call
  // ==========================================
  const handleStartCall = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    try {
      setCallState('dialing')
      setCallDuration(0)
      setDtmfFeedback(null)
      stopSpeaking()
      stopCallRecording()

      stopRingRef.current = playRingbackTone()

      const res = await axios.post(`${baseUrl}/api/v1/voice/call/dispatch`, {
        phone_number: dialPhone,
        customer_name: customerName,
        amount: parseFloat(amount) || 14500,
        scenario: scenario,
        language: 'hinglish',
        voice_persona: voicePersona,
        transaction_id: currentTxnId,
        provider: 'free_webrtc_softphone'
      })

      const newSid = res.data.call_sid
      setActiveCallSid(newSid)
      setActiveCallDetails(res.data)

      setCallState('ringing')
      setTimeout(() => {
        if (stopRingRef.current) {
          stopRingRef.current()
          stopRingRef.current = null
        }
        setCallState('connected')
        playRealisticVoice(res.data.audio_url, res.data.transcript_hinglish)
        const pName = PERSONAS[voicePersona]?.name || 'Agent'
        setActionSuccess(`Connected to ${dialPhone}! Neural Voice Agent (${pName}) active.`)
        fetchCalls()
        fetchQueue()
      }, 2200)
    } catch (err) {
      console.error(err)
      if (stopRingRef.current) stopRingRef.current()
      setCallState('idle')
    }
  }

  // ==========================================
  // 6. In-Call DTMF Keypress (Press 1, 2, 3)
  // ==========================================
  const handleInCallDTMF = async (digit: string) => {
    playDTMF(digit)

    if (callState === 'connected' && activeCallSid) {
      try {
        const res = await axios.post(`${baseUrl}/api/v1/voice/call/dtmf`, {
          call_sid: activeCallSid,
          digit: digit,
          customer_phone: dialPhone,
          customer_name: customerName,
          amount: parseFloat(amount) || 14500,
          voice_persona: voicePersona
        })

        if (digit === '1') {
          setDtmfFeedback('Key 1 Pressed: 1-Click WhatsApp & SMS Payment Link Dispatched! (Status: RECOVERED)')
          await saveCallRecord(activeCallSid, 'recovered')
        } else if (digit === '2') {
          setDtmfFeedback('Key 2 Pressed: Promise-to-Pay (PTP) Commitment Registered for +3 days! (Status: PTP COMMITTED)')
          await saveCallRecord(activeCallSid, 'ptp_committed')
        } else {
          setDtmfFeedback('Key 3 Pressed: Transferred to Priority Fintech Escalation Desk.')
          await saveCallRecord(activeCallSid, 'completed')
        }

        if (res.data.ack_audio_url) {
          playRealisticVoice(res.data.ack_audio_url)
        }

        fetchCalls()
        fetchQueue()
      } catch (err) {
        console.error('DTMF post error', err)
      }
    }
  }

  // ==========================================
  // 7. End Call (Guaranteed Recording Save)
  // ==========================================
  const handleEndCall = async () => {
    if (stopRingRef.current) {
      stopRingRef.current()
      stopRingRef.current = null
    }
    stopSpeaking()

    const sidToSave = activeCallSid
    if (sidToSave) {
      await saveCallRecord(sidToSave)
    }

    setCallState('ended')
    setTimeout(() => {
      setCallState('idle')
      setActiveCallSid(null)
      fetchCalls()
      fetchQueue()
    }, 1200)
  }

  // ==========================================
  // 8. 1-Click Call from Pending / Failed Queue
  // ==========================================
  const handleCallFromQueue = (item: any) => {
    setDialPhone(item.customer_phone)
    setCustomerName(item.customer_name)
    setAmount(item.amount.toString())
    setScenario(item.recommended_scenario)
    setVoicePersona(item.recommended_persona)
    setCurrentTxnId(item.transaction_id)

    // Scroll smoothly to dialer
    if (dialerCardRef.current) {
      dialerCardRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    // Auto-trigger call after brief delay
    setTimeout(() => {
      handleStartCall()
    }, 400)
  }

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60)
    const s = sec % 60
    return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const selectedPersona = PERSONAS[voicePersona] || PERSONAS['priya']

  return (
    <AppShell title="AI Voice Agent & WebRTC Telephony Console">
      <div className="space-y-6">
        {/* Top Header & Overview */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-pink-900 via-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="absolute -right-8 -top-8 w-60 h-60 bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="space-y-1 relative z-10">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-pink-500/20 text-pink-300 border border-pink-500/30 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> 5 Studio Neural Voices
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Call Recordings Enabled
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                ₹0.00 Free Telephony
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">
              AI Voice Recovery & Softphone Calling System
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm max-w-2xl">
              Outbound recovery calling queue for pending and failed transactions. Listen to call recordings across all history, select from 5 distinct human voice personas, and capture Promise-to-Pay commitments.
            </p>
          </div>

          <div className="flex items-center gap-2 relative z-10">
            <button
              onClick={() => { fetchCalls(); fetchQueue(); }}
              className="px-3 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading || queueLoading ? 'animate-spin' : ''}`} />
              Sync Data
            </button>
          </div>
        </div>

        {/* Global Feedback Banner */}
        {actionSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-semibold flex items-center justify-between animate-in fade-in">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{actionSuccess}</span>
            </div>
            <button 
              onClick={() => setActionSuccess(null)}
              className="text-emerald-700 hover:text-emerald-900 text-xs font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Metric KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
              <span>Total Calls Dispatched</span>
              <PhoneCall className="w-4 h-4 text-pink-600" />
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {data?.summary?.total_calls_initiated || 0}
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              100% Free WebRTC Softphone
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
              <span>Voice Recovered Rate</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <p className="text-2xl font-bold text-emerald-600 mt-1">
              {data?.summary?.call_completion_rate || 0}%
            </p>
            <p className="text-[11px] text-emerald-700 mt-0.5 font-medium">
              {data?.summary?.recovered_calls || 0} Recovered via 1-Click Link
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
              <span>Promise-to-Pay Secured</span>
              <CalendarCheck className="w-4 h-4 text-pink-600" />
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              ₹{((data?.summary?.ptp_captured_value || 0) / 100000).toFixed(2)} L
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5">
              {data?.summary?.ptp_calls || 0} customer commitments
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
              <span>Pending & Failed at Risk</span>
              <AlertTriangle className="w-4 h-4 text-amber-500" />
            </div>
            <p className="text-2xl font-bold text-amber-600 mt-1">
              ₹{((queueData?.summary?.total_at_risk_amount || 0) / 100000).toFixed(1)} L
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5">
              {queueData?.summary?.failed_transactions_count || 0} failed · {queueData?.summary?.pending_transactions_count || 0} pending
            </p>
          </div>
        </div>

        {/* Middle Section: Softphone Dialer & Active Call Screen */}
        <div ref={dialerCardRef} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column (5 Cols): Interactive Dialer & Voice Persona Selector */}
          <div className="lg:col-span-5 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-pink-100 flex items-center justify-center text-pink-600">
                  <Smartphone className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900">WebRTC Softphone Dialer</h2>
                  <p className="text-[11px] text-slate-500">Outbound call dispatcher</p>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">
                GATEWAY ONLINE
              </span>
            </div>

            {/* Dialpad Display Screen */}
            <div className="bg-slate-950 rounded-2xl p-4 text-center space-y-1 shadow-inner">
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span className="flex items-center gap-1">
                  <span className={`w-2 h-2 rounded-full ${callState === 'connected' ? 'bg-emerald-500 animate-pulse' : callState === 'ringing' ? 'bg-amber-500 animate-ping' : 'bg-slate-500'}`} />
                  {callState.toUpperCase()}
                </span>
                <span className="font-mono text-emerald-400 font-bold">
                  {callState === 'connected' ? formatSeconds(callDuration) : '₹0.00 FREE'}
                </span>
              </div>
              <p className="text-xl font-mono font-bold text-white tracking-wider pt-1">
                {dialPhone}
              </p>
              <p className="text-[11px] text-slate-400 truncate">
                {customerName} · ₹{parseFloat(amount || '0').toLocaleString('en-IN')}
              </p>
              {currentTxnId && (
                <p className="text-[9px] font-mono text-pink-400">
                  Txn Ref: {currentTxnId}
                </p>
              )}
            </div>

            {/* Customer & Call Parameters */}
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Customer Phone</label>
                  <input
                    type="tel"
                    value={dialPhone}
                    onChange={(e) => setDialPhone(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Amount (₹)</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Recovery Scenario</label>
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-pink-500 bg-white"
                >
                  <option value="failed_call">🔴 Failed Payment Recovery (Bank Error / Declined)</option>
                  <option value="pending_call">🟡 Pending Payment Pre-Emptive Confirmation</option>
                  <option value="payment_retry">⚡ 1-Click Instant UPI Payment Retry</option>
                  <option value="salary_pending">📅 Salary Pending / Weekend PTP Commitment</option>
                  <option value="mandate_failure">💳 Subscription Mandate Auto-Debit Notice</option>
                </select>
              </div>

              {/* 5 Realistic Voice Personas Selector */}
              <div>
                <label className="font-semibold text-slate-700 block mb-1.5 flex items-center justify-between">
                  <span>Realistic Voice Persona ({Object.keys(PERSONAS).length} Available)</span>
                  <span className="text-[10px] text-pink-600 font-bold bg-pink-50 px-1.5 py-0.5 rounded">
                    Studio Neural HD
                  </span>
                </label>
                <div className="grid grid-cols-5 gap-1.5">
                  {Object.values(PERSONAS).map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => setVoicePersona(p.id)}
                      className={`p-1.5 rounded-xl border text-center transition flex flex-col items-center justify-center relative group ${
                        voicePersona === p.id
                          ? 'bg-pink-50 border-pink-500 text-pink-900 ring-2 ring-pink-500 font-bold shadow-xs'
                          : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <span className="text-base mb-0.5">{p.emoji}</span>
                      <span className="font-bold text-[11px] leading-tight truncate w-full">{p.name}</span>
                      <span className="text-[8px] text-slate-400 truncate w-full">{p.gender}</span>
                      
                      {/* Audio Sample Preview Mini Button */}
                      <span 
                        onClick={(e) => previewPersonaVoice(p.id, e)}
                        title="Listen to voice sample"
                        className="mt-1 w-4 h-4 rounded-full bg-slate-100 hover:bg-pink-200 text-slate-600 hover:text-pink-700 flex items-center justify-center"
                      >
                        <Volume2 className="w-2.5 h-2.5" />
                      </span>
                    </button>
                  ))}
                </div>
                <p className="text-[10px] text-slate-500 mt-1 italic">
                  Active: <strong>{selectedPersona.name}</strong> ({selectedPersona.title}) · {selectedPersona.badge}
                </p>
              </div>

              {/* Audio Mode: Studio HD vs Cellular Handset Filter */}
              <div className="pt-1 flex items-center justify-between bg-slate-50 p-2 rounded-xl border border-slate-200">
                <div className="flex items-center gap-1.5 text-[11px]">
                  <span>{telephonyFilter ? '📱' : '🎧'}</span>
                  <span className="font-semibold text-slate-800">
                    {telephonyFilter ? 'Cellular Handset Filter (3.4kHz Bandpass)' : 'Studio HD Quality (Crystal Clear)'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setTelephonyFilter(!telephonyFilter)}
                  className={`px-2 py-0.5 text-[10px] font-bold rounded-lg transition border ${
                    telephonyFilter
                      ? 'bg-amber-100 text-amber-800 border-amber-300'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {telephonyFilter ? 'Filter ON' : 'Enable Filter'}
                </button>
              </div>
            </div>

            {/* DTMF Dialpad Grid */}
            <div className="space-y-2">
              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider text-center">
                In-Call Interactive DTMF Keypad (With Audio Tones)
              </p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { num: '1', sub: '' },
                  { num: '2', sub: 'ABC' },
                  { num: '3', sub: 'DEF' },
                  { num: '4', sub: 'GHI' },
                  { num: '5', sub: 'JKL' },
                  { num: '6', sub: 'MNO' },
                  { num: '7', sub: 'PQRS' },
                  { num: '8', sub: 'TUV' },
                  { num: '9', sub: 'WXYZ' },
                  { num: '*', sub: '' },
                  { num: '0', sub: '+' },
                  { num: '#', sub: '' },
                ].map(({ num, sub }) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => handleInCallDTMF(num)}
                    className="py-2.5 bg-slate-50 hover:bg-slate-100 active:bg-pink-100 border border-slate-200 rounded-xl flex flex-col items-center justify-center transition shadow-2xs group"
                  >
                    <span className="text-base font-bold text-slate-800 group-hover:text-pink-600 font-mono">
                      {num}
                    </span>
                    {sub && <span className="text-[9px] text-slate-400">{sub}</span>}
                  </button>
                ))}
              </div>
            </div>

            {/* Call Action Triggers */}
            <div className="pt-2">
              {callState === 'idle' || callState === 'ended' ? (
                <button
                  type="button"
                  onClick={handleStartCall}
                  className="w-full py-3 bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 text-white font-bold text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition"
                >
                  <PhoneCall className="w-4 h-4" />
                  Initiate AI Recovery Call ({selectedPersona.name})
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleEndCall}
                  className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition animate-pulse"
                >
                  <PhoneOff className="w-4 h-4" />
                  Terminate Call ({formatSeconds(callDuration)})
                </button>
              )}
            </div>
          </div>

          {/* Right Column (7 Cols): Active Softphone Screen & Live Forensic Visualizer */}
          <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between space-y-4">
            <div>
              {/* Call Status Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${callState === 'connected' ? 'bg-emerald-500 animate-pulse' : callState === 'ringing' ? 'bg-amber-500 animate-ping' : 'bg-slate-300'}`} />
                  <span className="font-bold text-xs text-slate-800">
                    {callState === 'connected' && `Call Active with ${customerName} (${dialPhone})`}
                    {callState === 'dialing' && `Dialing ${dialPhone}...`}
                    {callState === 'ringing' && `Ringing Customer Phone...`}
                    {callState === 'ended' && `Call Completed & Commitment Logged`}
                    {callState === 'idle' && `Telephony Softphone Ready`}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] font-mono">
                    Voice: {selectedPersona.name} ({selectedPersona.gender})
                  </span>
                  <button
                    onClick={() => setSpeakerOn(!speakerOn)}
                    className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100"
                    title={speakerOn ? 'Mute speaker' : 'Unmute speaker'}
                  >
                    {speakerOn ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4 text-red-500" />}
                  </button>
                </div>
              </div>

              {/* Animated Neural Voice Equalizer Waveform */}
              <div className="mt-4 p-4 bg-slate-900 rounded-2xl flex flex-col items-center justify-center text-center space-y-3 shadow-inner">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{selectedPersona.emoji}</span>
                  <span className="text-xs font-bold text-white tracking-wide">
                    {selectedPersona.name} ({selectedPersona.title})
                  </span>
                  <span className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
                </div>

                {/* Animated 8-band Frequency Bars */}
                <div className="flex items-end justify-center gap-1.5 h-12 w-full max-w-xs">
                  {[40, 75, 95, 60, 85, 100, 70, 50].map((h, i) => (
                    <div
                      key={i}
                      className={`w-2 rounded-full transition-all duration-150 ${
                        isSpeaking 
                          ? 'bg-gradient-to-t from-pink-500 to-indigo-400 animate-pulse' 
                          : 'bg-slate-800'
                      }`}
                      style={{
                        height: isSpeaking ? `${Math.max(15, (h * Math.sin((i + 1) * 1.5)) % 48)}px` : '6px',
                        animationDelay: `${i * 90}ms`
                      }}
                    />
                  ))}
                </div>

                <div className="flex items-center justify-center gap-2">
                  <span className="text-[11px] font-mono text-pink-300">
                    {isSpeaking ? 'Agent Speaking with Expressive Inflection...' : callState === 'connected' ? 'Listening for Customer Input / DTMF...' : 'Softphone Idle'}
                  </span>
                  {activeCallDetails && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => playRealisticVoice(activeCallDetails.audio_url, activeCallDetails.transcript_hinglish)}
                        className="px-2 py-0.5 text-[10px] font-semibold bg-white/10 hover:bg-white/20 text-white rounded flex items-center gap-1 transition"
                      >
                        <Play className="w-3 h-3" /> Replay
                      </button>

                      <button
                        onClick={() => activeCallSid && saveCallRecord(activeCallSid)}
                        disabled={isSavingRecording}
                        className="px-2.5 py-0.5 text-[10px] font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded flex items-center gap-1 shadow-xs transition"
                      >
                        <span>💾</span> {isSavingRecording ? 'Saving...' : 'Save Recording'}
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* In-Call DTMF Interactive Menu Guide */}
              <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span className="text-[11px] font-bold text-slate-900 block">
                  Customer Interactive DTMF Keypad Actions:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => handleInCallDTMF('1')}
                    className="p-2 bg-white border border-slate-200 rounded-lg hover:border-emerald-400 text-left transition group"
                  >
                    <span className="font-bold text-emerald-600 font-mono flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> Press 1:
                    </span>
                    <p className="text-[10px] text-slate-600 mt-0.5">Send 1-Click WhatsApp link (Recovered)</p>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleInCallDTMF('2')}
                    className="p-2 bg-white border border-slate-200 rounded-lg hover:border-pink-400 text-left transition group"
                  >
                    <span className="font-bold text-pink-600 font-mono flex items-center gap-1">
                      <CalendarCheck className="w-3 h-3" /> Press 2:
                    </span>
                    <p className="text-[10px] text-slate-600 mt-0.5">Promise-to-Pay (PTP scheduled)</p>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleInCallDTMF('3')}
                    className="p-2 bg-white border border-slate-200 rounded-lg hover:border-amber-400 text-left transition group"
                  >
                    <span className="font-bold text-amber-600 font-mono flex items-center gap-1">
                      <PhoneForwarded className="w-3 h-3" /> Press 3:
                    </span>
                    <p className="text-[10px] text-slate-600 mt-0.5">Connect to Live Senior Desk</p>
                  </button>
                </div>

                {dtmfFeedback && (
                  <div className="p-2 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-[11px] font-semibold flex items-center gap-1.5 animate-in fade-in">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>{dtmfFeedback}</span>
                  </div>
                )}
              </div>

              {/* Dialogue Transcript Stream */}
              <div className="mt-4 space-y-3">
                <div className="p-4 bg-slate-900 text-slate-100 rounded-2xl shadow-inner space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-pink-400 font-semibold border-b border-slate-800 pb-1.5">
                    <span>Hinglish Code-Switched Voice Transcript</span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {activeCallDetails?.call_sid || 'CA_live_session'}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm leading-relaxed text-slate-200 font-sans whitespace-pre-line">
                    {activeCallDetails?.transcript_hinglish || 
                      `Namaste ${customerName} ji! Main UrbanKart Priority Recovery desk se ${selectedPersona.name} baat kar raha hoon. Aapka ₹${parseFloat(amount || '0').toLocaleString('en-IN')} ka payment bank timeout ki wajah se hold pe tha. Instant 1-click link ke liye 1 dabayein, ya payment schedule karne ke liye 2 dabayein.`
                    }
                  </p>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                    English Forensic Intent Translation
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed italic">
                    "{activeCallDetails?.transcript_english || 
                      `Hello ${customerName}! This is ${selectedPersona.name} from UrbanKart Priority Recovery desk. Your transaction was interrupted by a bank network decline. Press 1 for 1-click link, or Press 2 to schedule payment.`
                    }"
                  </p>
                </div>
              </div>
            </div>

            {/* Compliance Note */}
            <div className="p-3 bg-emerald-50/60 border border-emerald-200 rounded-xl text-[11px] text-emerald-900 flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>
                <strong>NPCI & TRAI Compliance</strong>: Standard quiet hours enforced (08:00 - 21:00 IST). WebRTC free in-browser calling with zero third-party phone provider bills.
              </span>
            </div>
          </div>
        </div>

        {/* SECTION: Outbound Calling Queue According to Pending & Failed Calls */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-900">
                  Outbound Calling Queue: Pending & Failed Payment Worklist
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-pink-100 text-pink-800 rounded-full">
                  {queueData?.items?.length || 0} In Worklist
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Actionable recovery queue partitioned by failed transactions and pending debits. 1-click dials the customer with AI recommended scenario & persona.
              </p>
            </div>

            {/* Search & Filter Bar */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search customer, phone, or Txn ID..."
                  value={queueSearch}
                  onChange={(e) => setQueueSearch(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg w-56 focus:outline-none focus:ring-1 focus:ring-pink-500"
                />
              </div>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="px-6 py-2 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center gap-2">
            {[
              { id: 'all', label: 'All Calling Worklist', count: queueData?.summary?.total_in_queue || 0 },
              { id: 'failed', label: '🔴 Failed Payment Retries', count: queueData?.summary?.failed_transactions_count || 0 },
              { id: 'pending', label: '🟡 Pending Debits & Dropoffs', count: queueData?.summary?.pending_transactions_count || 0 },
              { id: 'recovered', label: '🟢 Recovered via Voice', count: queueData?.summary?.recovered_calls_count || 0 },
              { id: 'ptp', label: '🟣 Promise-to-Pay (PTP)', count: queueData?.summary?.ptp_calls_count || 0 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setQueueFilter(tab.id as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                  queueFilter === tab.id
                    ? 'bg-white text-slate-900 shadow-xs border border-slate-300'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <span>{tab.label}</span>
                <span className="px-1.5 py-0.2 bg-slate-200 text-slate-700 rounded-full text-[10px]">
                  {tab.count}
                </span>
              </button>
            ))}
          </div>

          {/* Queue Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Customer & Phone</th>
                  <th className="px-4 py-3">Transaction / Bank</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Failure / Pending Reason</th>
                  <th className="px-4 py-3">Recommended Voice Persona</th>
                  <th className="px-4 py-3">Last Call Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {queueLoading && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-slate-400">
                      Loading outbound calling queue...
                    </td>
                  </tr>
                )}
                {!queueLoading && queueData?.items?.map((item: any) => {
                  const personaObj = PERSONAS[item.recommended_persona] || PERSONAS['priya']
                  return (
                    <tr key={item.transaction_id} className="hover:bg-slate-50/80 transition">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700 text-xs">
                            {item.customer_name[0]}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900">{item.customer_name}</p>
                            <p className="text-[10px] text-slate-500">{item.customer_phone}</p>
                          </div>
                        </div>
                      </td>

                      <td className="px-4 py-3">
                        <p className="font-mono text-[11px] font-semibold text-slate-800">{item.transaction_id}</p>
                        <p className="text-[10px] text-slate-500">{item.bank_name} · {item.payment_method.toUpperCase()}</p>
                      </td>

                      <td className="px-4 py-3 font-mono font-bold text-slate-900">
                        ₹{item.amount.toLocaleString('en-IN')}
                      </td>

                      <td className="px-4 py-3">
                        {item.transaction_status === 'FAILED' ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200 flex items-center gap-1 w-max">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            FAILED
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1 w-max">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                            PENDING
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3">
                        <p className="font-medium text-slate-800 text-[11px]">{item.failure_reason}</p>
                        <p className="text-[10px] text-slate-400 font-mono">{item.failure_code}</p>
                      </td>

                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-pink-50 text-pink-800 border border-pink-200 text-[11px] font-semibold">
                          <span>{personaObj.emoji}</span>
                          <span>{personaObj.name}</span>
                          <span className="text-[9px] text-pink-600">({personaObj.title.split(' ')[0]})</span>
                        </span>
                      </td>

                      <td className="px-4 py-3">
                        {item.current_call_status === 'recovered' ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 flex items-center gap-1 w-max">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> RECOVERED
                          </span>
                        ) : item.current_call_status === 'ptp_committed' ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 flex items-center gap-1 w-max">
                            <CalendarCheck className="w-3 h-3 text-purple-600" /> PTP SCHEDULED
                          </span>
                        ) : item.current_call_status === 'failed_unreachable' ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 flex items-center gap-1 w-max">
                            <AlertCircle className="w-3 h-3 text-red-600" /> UNREACHABLE
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600">
                            Uncalled
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={() => handleCallFromQueue(item)}
                          className="px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold rounded-lg shadow-xs flex items-center gap-1 text-[11px] ml-auto transition"
                        >
                          <PhoneCall className="w-3 h-3" />
                          Call Customer
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* SECTION: Call History & Audio Call Recordings Ledger */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-slate-900">
                  Voice Recovery Call History & Audio Recordings Ledger
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded-full">
                  {data?.items?.length || 0} Recorded Sessions
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Complete call audio recordings, forensic Hinglish transcripts, customer objections, and Promise-to-Pay commits.
              </p>
            </div>

            {/* Filters Bar */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by SID or Phone..."
                  value={historySearch}
                  onChange={(e) => setHistorySearch(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg w-48 focus:outline-none focus:ring-1 focus:ring-pink-500"
                />
              </div>

              <select
                value={historyPersonaFilter}
                onChange={(e) => setHistoryPersonaFilter(e.target.value)}
                className="px-2.5 py-1.5 text-xs border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-pink-500"
              >
                <option value="all">All Personas</option>
                <option value="priya">👩‍💼 Priya</option>
                <option value="rahul">👨‍💼 Rahul</option>
                <option value="swara">🇮🇳 Swara</option>
                <option value="madhur">🎙️ Madhur</option>
                <option value="kavya">🌸 Kavya</option>
              </select>

              <select
                value={historyStatusFilter}
                onChange={(e) => setHistoryStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 text-xs border border-slate-200 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-pink-500"
              >
                <option value="all">All Statuses</option>
                <option value="recovered">Recovered via Link</option>
                <option value="ptp_committed">PTP Committed</option>
                <option value="failed_unreachable">Unreachable</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Call SID & Persona</th>
                  <th className="px-4 py-3">Customer Phone</th>
                  <th className="px-4 py-3">Call Audio Recording</th>
                  <th className="px-4 py-3">Duration</th>
                  <th className="px-4 py-3">Detected Objection</th>
                  <th className="px-4 py-3">PTP Commitment</th>
                  <th className="px-4 py-3">Call Outcome</th>
                  <th className="px-4 py-3 text-right">Transcript</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {loading && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-slate-400">
                      Loading recorded calls...
                    </td>
                  </tr>
                )}
                {!loading && data?.items?.map((call: any) => {
                  const pObj = PERSONAS[call.voice_persona] || PERSONAS['priya']
                  const isPlaying = playingRecordingSid === call.call_sid
                  const isExpanded = expandedCallId === call.id

                  return (
                    <React.Fragment key={call.id}>
                      <tr className={`transition ${call.call_sid === lastSavedCallSid ? 'bg-emerald-50/90 ring-2 ring-emerald-500 font-semibold shadow-xs' : 'hover:bg-slate-50/80'}`}>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            <p className="font-mono text-[11px] font-bold text-slate-900">{call.call_sid}</p>
                            {call.call_sid === lastSavedCallSid && (
                              <span className="px-1.5 py-0.2 rounded-full bg-emerald-600 text-white text-[9px] font-bold animate-pulse">
                                JUST SAVED
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-1 mt-0.5">
                            <span>{pObj.emoji}</span>
                            <span className="text-[10px] text-pink-700 font-semibold">{pObj.name}</span>
                          </div>
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          <p className="font-semibold text-slate-900">{call.customer_name}</p>
                          <p className="text-[10px] text-slate-500 font-mono">{call.customer_phone}</p>
                        </td>

                        {/* Interactive Call Recording Player */}
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200 w-max">
                            <button
                              type="button"
                              onClick={() => togglePlayRecording(call.recording_url, call.call_sid)}
                              className={`w-7 h-7 rounded-lg flex items-center justify-center transition shadow-2xs ${
                                isPlaying 
                                  ? 'bg-pink-600 text-white animate-pulse' 
                                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
                              }`}
                              title={isPlaying ? 'Pause call recording' : 'Play call recording'}
                            >
                              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current ml-0.5" />}
                            </button>

                            {/* Mini Waveform & Status */}
                            <div className="flex items-center gap-1 px-1">
                              {[10, 16, 22, 14, 18, 24, 12].map((h, i) => (
                                <span
                                  key={i}
                                  className={`w-1 rounded-full transition-all duration-150 ${
                                    isPlaying ? 'bg-pink-500 animate-pulse' : 'bg-slate-300'
                                  }`}
                                  style={{ height: isPlaying ? `${(h * 1.2)}px` : '6px' }}
                                />
                              ))}
                            </div>

                            {/* Download Recording Link */}
                            <a
                              href={call.recording_url}
                              download={`Call_${call.call_sid}.mp3`}
                              className="p-1.5 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-200"
                              title="Download MP3 Call Recording"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </a>
                          </div>
                        </td>

                        <td className="px-4 py-3 font-mono text-slate-600 whitespace-nowrap">
                          {formatSeconds(call.duration_seconds || 45)}
                        </td>

                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 font-medium text-[10px]">
                            {call.detected_objection}
                          </span>
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          {call.captured_ptp_date ? (
                            <div>
                              <p className="font-semibold text-pink-600 text-[11px]">
                                {new Date(call.captured_ptp_date).toLocaleDateString()}
                              </p>
                              <p className="text-[10px] text-slate-400 font-mono">
                                ₹{(call.captured_ptp_amount || 0).toLocaleString('en-IN')}
                              </p>
                            </div>
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          {call.call_status === 'recovered' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              RECOVERED
                            </span>
                          ) : call.call_status === 'ptp_committed' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800">
                              <CalendarCheck className="w-3 h-3 text-purple-600" />
                              PTP COMMITTED
                            </span>
                          ) : call.call_status === 'failed_unreachable' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800">
                              <AlertCircle className="w-3 h-3 text-red-600" />
                              UNREACHABLE
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">
                              COMPLETED
                            </span>
                          )}
                        </td>

                        <td className="px-4 py-3 text-right whitespace-nowrap">
                          <button
                            type="button"
                            onClick={() => setExpandedCallId(isExpanded ? null : call.id)}
                            className="px-2.5 py-1 text-[11px] font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg inline-flex items-center gap-1 transition"
                          >
                            <FileText className="w-3 h-3" />
                            {isExpanded ? 'Hide' : 'Transcript'}
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        </td>
                      </tr>

                      {/* Expandable Forensic Transcript Row */}
                      {isExpanded && (
                        <tr className="bg-slate-50/90 border-b border-slate-200">
                          <td colSpan={8} className="px-6 py-4 space-y-3">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                              <div className="p-3 bg-slate-900 text-slate-100 rounded-xl space-y-1">
                                <span className="text-[10px] text-pink-400 font-bold uppercase tracking-wider block">
                                  Hinglish Dialogue (Agent: {pObj.name})
                                </span>
                                <p className="leading-relaxed whitespace-pre-line text-slate-200">
                                  {call.transcript_hinglish}
                                </p>
                              </div>

                              <div className="p-3 bg-white border border-slate-200 rounded-xl space-y-1">
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                                  English Forensic Intent & Translation
                                </span>
                                <p className="leading-relaxed italic text-slate-700">
                                  "{call.transcript_english}"
                                </p>
                                <div className="pt-2 border-t border-slate-100 mt-2 flex items-center justify-between text-[10px] text-slate-500">
                                  <span>Intent: <strong>{call.detected_intent}</strong></span>
                                  <span>Recorded Audio: <code>{call.recording_url}</code></span>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  )
}
