import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/solid'
import api from '../services/api'
import voiceService from '../services/voiceService'
import VoiceInput from './VoiceInput'

export default function ChatInterface({ onCommandGenerated, onShowConfirmation }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your Personal AI Agent. I can help you manage your Windows system safely. What would you like me to do?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await api.sendMessage(input)

      if (response.success) {
        // Add command response
        const commandMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.explanation || 'I\'ve generated a command for your request.',
          command: response.command,
          risks: response.risks,
          is_safe: response.is_safe,
          suggestions: response.suggestions,
          optimizations: response.optimizations,
          timestamp: new Date()
        }

        setMessages(prev => [...prev, commandMessage])
        
        // Speak response if voice enabled
        if (voiceEnabled && response.explanation) {
          speakMessage(response.explanation);
        }
        
        // Pass command to parent
        onCommandGenerated(response)
      } else {
        // Error message
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'error',
          content: response.error || 'Failed to process your request',
          timestamp: new Date()
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const speakMessage = async (text) => {
    if (isSpeaking) {
      voiceService.stopSpeaking();
      setIsSpeaking(false);
      return;
    }

    try {
      setIsSpeaking(true);
      await voiceService.speak(text);
      setIsSpeaking(false);
    } catch (error) {
      console.error('Speech error:', error);
      setIsSpeaking(false);
    }
  };

  const handleVoiceInput = (transcript) => {
    setInput(transcript);
  };

  const handleVoiceFinal = (transcript) => {
    setInput(transcript);
    // Auto-send after voice input
    setTimeout(() => {
      if (transcript.trim()) {
        handleSend();
      }
    }, 300);
  };

  const toggleVoice = () => {
    if (isSpeaking) {
      voiceService.stopSpeaking();
      setIsSpeaking(false);
    }
    setVoiceEnabled(!voiceEnabled);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="animate-fadeIn">
            {message.type === 'user' ? (
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-2xl">
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ) : message.type === 'error' ? (
              <div className="flex justify-start">
                <div className="bg-red-500/20 border border-red-500 text-red-400 px-4 py-2 rounded-lg max-w-2xl">
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ) : (
              <div className="flex justify-start">
                <div className="bg-slate-800 text-slate-200 px-4 py-3 rounded-lg max-w-2xl space-y-2">
                  <p className="text-sm">{message.content}</p>
                  
                  {message.command && (
                    <div className="mt-2 space-y-2">
                      {/* Command Preview */}
                      <div className="bg-slate-900 p-3 rounded border border-slate-700">
                        <p className="text-xs text-slate-400 mb-1">Generated Command:</p>
                        <code className="text-xs text-cyan-400 font-mono">{message.command}</code>
                      </div>

                      {/* Risks */}
                      {message.risks && message.risks.length > 0 && (
                        <div className={`p-2 rounded text-xs ${
                          message.is_safe ? 'bg-yellow-500/10 text-yellow-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                          <p className="font-medium mb-1">⚠️ Warnings:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {message.risks.map((risk, i) => (
                              <li key={i}>{risk}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="bg-blue-500/10 text-blue-400 p-2 rounded text-xs">
                          <p className="font-medium mb-1">💡 Suggestions:</p>
                          <ul className="space-y-1">
                            {message.suggestions.map((sug, i) => (
                              <li key={i}>
                                {sug.command} ({(sug.confidence * 100).toFixed(0)}% confidence)
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Action Button */}
                      <button
                        onClick={onShowConfirmation}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-2 px-4 rounded transition-colors"
                      >
                        Review & Execute
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-400 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-700 bg-slate-800 px-6 py-4">
        <div className="flex items-center space-x-2 mb-2">
          <button
            onClick={toggleVoice}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              voiceEnabled
                ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
            }`}
            title={voiceEnabled ? 'Voice responses enabled' : 'Voice responses disabled'}
          >
            {voiceEnabled ? (
              <><SpeakerWaveIcon className="w-4 h-4 inline mr-1" />Voice On</>
            ) : (
              <><SpeakerXMarkIcon className="w-4 h-4 inline mr-1" />Voice Off</>
            )}
          </button>
          {isSpeaking && (
            <span className="text-xs text-green-400 animate-pulse">Speaking...</span>
          )}
        </div>
        <div className="flex items-end space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your system... (or use voice input)"
            disabled={isLoading}
            className="flex-1 bg-slate-900 text-white border border-slate-700 rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            rows="3"
          />
          <div className="flex flex-col space-y-2">
            <VoiceInput
              onTranscript={handleVoiceInput}
              onFinalTranscript={handleVoiceFinal}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white p-3 rounded-lg transition-colors disabled:cursor-not-allowed"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
