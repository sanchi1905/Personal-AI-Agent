import { useState, useEffect, useRef } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
const MAX_RECONNECT_ATTEMPTS = 10
const INITIAL_RECONNECT_DELAY = 1000 // 1 second

export function useWebSocket() {
  const [connected, setConnected] = useState(false)
  const [systemUpdate, setSystemUpdate] = useState(null)
  const [executionUpdate, setExecutionUpdate] = useState(null)
  const ws = useRef(null)
  const reconnectAttempts = useRef(0)
  const reconnectTimeout = useRef(null)

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  const connect = () => {
    // Don't try to connect if we've exceeded max attempts
    if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
      console.log('Max WebSocket reconnection attempts reached')
      return
    }

    try {
      ws.current = new WebSocket(WS_URL)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setConnected(true)
        reconnectAttempts.current = 0 // Reset on successful connection
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)
        
        // Exponential backoff for reconnection
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.min(
            INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts.current),
            30000 // Max 30 seconds
          )
          
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${MAX_RECONNECT_ATTEMPTS})`)
          
          reconnectTimeout.current = setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, delay)
        }
      }

      ws.current.onerror = (error) => {
        console.warn('WebSocket error (non-fatal):', error.message || 'Connection failed')
        // Don't crash the app on WebSocket errors
      }

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          switch (data.type) {
            case 'system_update':
              setSystemUpdate(data.data)
              break
            
            case 'execution_start':
            case 'execution_complete':
            case 'execution_error':
              setExecutionUpdate(data)
              break
            
            default:
              console.log('Unknown message type:', data.type)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }

  return {
    connected,
    systemUpdate,
    executionUpdate,
  }
}
