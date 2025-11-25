import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Upload, X, Loader2, Camera, Image as ImageIcon } from 'lucide-react'
import api from '../lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  imageUrl?: string
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
  const [showCamera, setShowCamera] = useState(false)
  const [isProcessingImage, setIsProcessingImage] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

  // Cleanup camera stream on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }
  }, [])

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

  const handleImageUpload = async (file: File) => {
    if (!file) return

    if (file.size > 10 * 1024 * 1024) {
      alert('Image size must be less than 10MB')
      return
    }

    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (JPG, PNG, etc.)')
      return
    }

    setIsProcessingImage(true)

    try {
      // Create preview URL
      const imageUrl = URL.createObjectURL(file)

      // Add user message with image
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: `📷 Image uploaded: ${file.name}`,
        timestamp: new Date(),
        imageUrl: imageUrl,
      }
      setMessages((prev) => [...prev, userMessage])

      // Upload to OCR endpoint
      const formData = new FormData()
      formData.append('image', file)
      formData.append('domain', selectedDomain)
      formData.append('language', selectedLanguage)
      formData.append('analyze', 'true') // Backend expects string 'true' for Form field

      setLoading(true)

      try {
        // Don't set Content-Type header - axios will set it automatically with boundary for FormData
        const response = await api.post('/public/ocr', formData, {
          timeout: 60000, // 60 second timeout for OCR processing
        })

        const ocrData = response.data

        // Show extracted text
        if (ocrData.extracted_text && ocrData.extracted_text.trim()) {
          const extractedMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `**📄 Extracted Text:**\n${ocrData.extracted_text}\n\n**Document Type:** ${ocrData.document_type || 'Unknown'}\n**Confidence:** ${((ocrData.confidence || 0) * 100).toFixed(1)}%`,
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, extractedMessage])
        } else {
          const noTextMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '⚠️ No text could be extracted from this image. Please ensure the image is clear and contains readable text.',
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, noTextMessage])
        }

        // Show AI analysis if available
        if (ocrData.analysis) {
          const analysisMessage: Message = {
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: formatResponse(ocrData.analysis),
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, analysisMessage])
        } else if (ocrData.analysis_error) {
          const errorAnalysisMessage: Message = {
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: `⚠️ Text extracted but AI analysis failed: ${ocrData.analysis_error}`,
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, errorAnalysisMessage])
        }
      } catch (uploadError: any) {
        console.error('Image upload error:', uploadError)
        throw uploadError // Re-throw to be caught by outer catch
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error processing the image: ${error.response?.data?.detail || error.message}. Please try again.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsProcessingImage(false)
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Handle images
    if (file.type.startsWith('image/')) {
      await handleImageUpload(file)
      return
    }

    // Handle other file types (text files)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    try {
      if (file.type === 'text/plain') {
        const text = await file.text()
        setInput((prev) => prev + (prev ? '\n\n' : '') + `[Document: ${file.name}]\n${text}`)
      } else {
        alert('Please upload an image file for OCR or a text file.')
      }
    } catch (error) {
      console.error('File upload error:', error)
      alert('Failed to process document')
    }
  }

  const startCamera = async () => {
    try {
      // First, try to enumerate devices to find external/USB cameras
      let videoConstraints: MediaTrackConstraints = {
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }

      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoInputs = devices.filter(device => device.kind === 'videoinput')
        
        // Prefer external/USB cameras (usually have longer labels or specific names)
        // On Jetson Nano, USB cameras are typically listed separately
        const externalCamera = videoInputs.find(device => 
          device.label && (
            device.label.toLowerCase().includes('usb') ||
            device.label.toLowerCase().includes('external') ||
            device.label.toLowerCase().includes('camera') ||
            device.label.toLowerCase().includes('webcam') ||
            device.label.toLowerCase().includes('logitech') ||
            device.label.toLowerCase().includes('hd') ||
            // Jetson Nano specific camera names
            device.label.toLowerCase().includes('uvc') ||
            device.label.toLowerCase().includes('video')
          )
        )

        if (externalCamera && externalCamera.deviceId) {
          // Use external camera device ID
          videoConstraints.deviceId = { exact: externalCamera.deviceId }
          console.log('Using external camera:', externalCamera.label)
        } else if (videoInputs.length > 1) {
          // If multiple cameras, prefer the last one (usually external on Jetson Nano)
          const lastCamera = videoInputs[videoInputs.length - 1]
          if (lastCamera.deviceId) {
            videoConstraints.deviceId = { exact: lastCamera.deviceId }
            console.log('Using camera:', lastCamera.label || 'Camera ' + videoInputs.length)
          }
        } else if (videoInputs.length === 1 && videoInputs[0].deviceId) {
          // Only one camera available
          videoConstraints.deviceId = { exact: videoInputs[0].deviceId }
          console.log('Using available camera:', videoInputs[0].label || 'Camera')
        } else {
          // Fallback to facingMode for mobile devices
          videoConstraints.facingMode = 'environment'
        }
      } catch (enumError) {
        console.warn('Could not enumerate devices, using default camera:', enumError)
        // Fallback to facingMode
        videoConstraints.facingMode = 'environment'
      }

      // Request camera access with selected constraints
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints
      })
      
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          if (videoRef.current) {
            videoRef.current.play().catch(err => {
              console.error('Error playing video:', err)
            })
          }
        }
      }
      setShowCamera(true)
    } catch (error: any) {
      console.error('Error accessing camera:', error)
      if (error.name === 'NotAllowedError') {
        alert('Camera access denied. Please enable camera permissions in your browser settings.')
      } else if (error.name === 'NotFoundError') {
        alert('No camera found. Please connect a camera and try again.')
      } else {
        alert(`Camera error: ${error.message || 'Unable to access camera'}`)
      }
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop()
      })
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
      videoRef.current.pause()
    }
    setShowCamera(false)
  }

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) {
      console.error('Video or canvas ref not available')
      return
    }

    const video = videoRef.current
    const canvas = canvasRef.current

    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready')
      alert('Please wait for camera to be ready')
      return
    }

    const context = canvas.getContext('2d')
    if (!context) {
      console.error('Could not get canvas context')
      return
    }

    // Set canvas dimensions to match video
    const videoWidth = video.videoWidth || 640
    const videoHeight = video.videoHeight || 480
    
    if (videoWidth === 0 || videoHeight === 0) {
      console.error('Invalid video dimensions')
      alert('Camera not ready. Please try again.')
      return
    }

    canvas.width = videoWidth
    canvas.height = videoHeight

    // Draw video frame to canvas
    try {
      context.drawImage(video, 0, 0, videoWidth, videoHeight)
    } catch (error) {
      console.error('Error drawing video to canvas:', error)
      alert('Failed to capture image. Please try again.')
      return
    }

    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
      if (blob) {
        stopCamera()
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
        await handleImageUpload(file)
      } else {
        console.error('Failed to create blob from canvas')
        alert('Failed to process captured image. Please try again.')
      }
    }, 'image/jpeg', 0.9)
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

      {/* Camera Modal */}
      {showCamera && (
        <div className="fixed inset-0 bg-black/80 z-50 flex flex-col items-center justify-center p-4">
          <div className="bg-white dark:bg-[#161B22] rounded-2xl p-4 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Capture Image</h3>
              <button
                onClick={stopCamera}
                className="p-2 hover:bg-gray-100 dark:hover:bg-[#0D1117] rounded-lg"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full rounded-lg mb-4 bg-black"
              style={{ maxHeight: '60vh', objectFit: 'contain' }}
              onLoadedMetadata={() => {
                if (videoRef.current) {
                  videoRef.current.play().catch(err => {
                    console.error('Error playing video:', err)
                  })
                }
              }}
            />
            <canvas ref={canvasRef} className="hidden" />
            <div className="flex gap-2">
              <button
                onClick={stopCamera}
                className="flex-1 px-4 py-2 bg-gray-200 dark:bg-[#0D1117] text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-[#161B22] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={captureImage}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-red-500 to-blue-500 text-white rounded-lg hover:from-red-600 hover:to-blue-600 transition-all"
              >
                Capture
              </button>
            </div>
          </div>
        </div>
      )}

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
              {message.imageUrl && (
                <img
                  src={message.imageUrl}
                  alt="Uploaded"
                  className="mb-2 rounded-lg max-w-full h-auto max-h-48 object-contain"
                />
              )}
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        {(loading || isProcessingImage) && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-[#0D1117] rounded-lg p-3">
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
            disabled={showCamera || isProcessingImage}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
          <button
            onClick={startCamera}
            className="p-2 bg-gray-200 dark:bg-[#161B22] hover:bg-gray-300 dark:hover:bg-[#0D1117] rounded-lg transition-colors"
            title="Capture Image with Camera"
            disabled={showCamera || isProcessingImage}
          >
            <Camera className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          <label className="p-2 bg-gray-200 dark:bg-[#161B22] hover:bg-gray-300 dark:hover:bg-[#0D1117] rounded-lg cursor-pointer transition-colors" title="Upload Image">
            <ImageIcon className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,.jpg,.jpeg,.png,.gif,.webp"
              onChange={handleFileUpload}
              className="hidden"
              disabled={showCamera || isProcessingImage}
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

