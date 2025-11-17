import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Upload, X, Loader2 } from 'lucide-react'
import api from '../lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatbotProps {
  onClose?: () => void
  initialQuery?: string
}

export default function Chatbot({ onClose, initialQuery }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m VU Legal AID assistant. How can I help you with your legal question today?',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState(initialQuery || '')
  const [loading, setLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [selectedDomain, setSelectedDomain] = useState('civil')
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Auto-send initial query if provided
  useEffect(() => {
    if (initialQuery && initialQuery.trim() && !loading) {
      // Small delay to ensure component is mounted
      const timer = setTimeout(() => {
        handleSend(initialQuery)
      }, 300)
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input
    if (!textToSend.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.post('/public/chat', {
        query_text: textToSend,
        domain: selectedDomain,
        language: selectedLanguage,
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: formatResponse(response.data),
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please try again.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const formatResponse = (data: any): string => {
    let formatted = `**Risk Assessment:** ${data.risk_level.toUpperCase()} (Score: ${data.risk_score}/100)\n\n`
    formatted += `**Analysis:**\n${data.analysis}\n\n`
    
    if (data.pros && data.pros.length > 0) {
      formatted += `**Pros:**\n${data.pros.map((p: string) => `• ${p}`).join('\n')}\n\n`
    }
    
    if (data.cons && data.cons.length > 0) {
      formatted += `**Cons:**\n${data.cons.map((c: string) => `• ${c}`).join('\n')}\n\n`
    }
    
    if (data.next_steps && data.next_steps.length > 0) {
      formatted += `**Next Steps:**\n${data.next_steps.map((s: string) => `→ ${s}`).join('\n')}\n\n`
    }
    
    if (data.lawyer_consultation_recommended) {
      formatted += `\n⚠️ **Professional lawyer consultation is recommended.**`
    }
    
    return formatted
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await handleAudioUpload(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Microphone access denied. Please enable microphone permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleAudioUpload = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')
      formData.append('language_hint', selectedLanguage)

      const response = await api.post('/ai/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setInput(response.data.text)
    } catch (error) {
      console.error('Transcription error:', error)
      alert('Failed to transcribe audio. Please try typing your question.')
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Extract text from document (simplified - would need backend endpoint)
      const text = await extractTextFromFile(file)
      if (text) {
        setInput((prev) => prev + (prev ? '\n\n' : '') + `[Document: ${file.name}]\n${text}`)
      }
    } catch (error) {
      console.error('File upload error:', error)
      alert('Failed to process document')
    }
  }

  const extractTextFromFile = async (file: File): Promise<string | null> => {
    // This is a placeholder - actual implementation would call backend
    if (file.type === 'text/plain') {
      return await file.text()
    }
    // For PDFs, would need backend processing
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white/95 dark:bg-[#161B22]/95 backdrop-blur-xl rounded-2xl shadow-2xl flex flex-col border border-gray-200/50 dark:border-gray-800/50" style={{ boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)' }}>
      {/* Header */}
      <div className="bg-gradient-to-r from-red-500 to-blue-500 text-white p-4 rounded-t-2xl flex justify-between items-center">
        <div>
          <h3 className="font-bold text-lg">VU Legal AID</h3>
          <p className="text-sm opacity-90">AI Legal Assistant</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="hover:bg-white/20 rounded p-1">
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Domain and Language Selectors */}
      <div className="p-3 bg-gray-50/50 dark:bg-[#0D1117]/50 border-b border-gray-200/50 dark:border-gray-800/50 flex gap-2">
        <select
          value={selectedDomain}
          onChange={(e) => setSelectedDomain(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-[#0D1117] text-gray-900 dark:text-gray-100"
        >
          <option value="agriculture">Agriculture</option>
          <option value="civil">Civil</option>
          <option value="family">Family</option>
          <option value="university">University</option>
        </select>
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          className="flex-1 px-2 py-1 text-sm border border-gray-200 dark:border-gray-800 rounded-lg bg-white dark:bg-[#0D1117] text-gray-900 dark:text-gray-100"
        >
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="ta">Tamil</option>
          <option value="te">Telugu</option>
          <option value="bn">Bengali</option>
          <option value="mr">Marathi</option>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-xl p-3 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-red-500 to-red-600 text-white'
                  : 'bg-gray-100 dark:bg-[#0D1117] text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200/50 dark:border-gray-800/50 bg-gray-50/50 dark:bg-[#0D1117]/50 rounded-b-2xl">
        <div className="flex gap-2 mb-2">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-2 rounded-lg transition-all ${
              isRecording 
                ? 'bg-red-500 text-white animate-pulse' 
                : 'bg-gray-200 dark:bg-[#161B22] hover:bg-gray-300 dark:hover:bg-[#0D1117] text-gray-700 dark:text-gray-300'
            }`}
            title="Voice Input"
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
          <label className="p-2 bg-gray-200 dark:bg-[#161B22] hover:bg-gray-300 dark:hover:bg-[#0D1117] rounded-lg cursor-pointer transition-colors" title="Upload Document">
            <Upload className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            <input
              type="file"
              accept=".pdf,.txt,.jpg,.jpeg,.png"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask your legal question..."
            className="flex-1 px-3 py-2 border border-gray-200 dark:border-gray-800 rounded-xl bg-white dark:bg-[#161B22] text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 dark:focus:ring-red-400/20 dark:focus:border-red-400"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-xl hover:from-red-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

