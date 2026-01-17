import { useState, useEffect, useRef } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocket() {
  const [connected, setConnected] = useState(false)
  const [systemUpdate, setSystemUpdate] = useState(null)
  const [executionUpdate, setExecutionUpdate] = useState(null)
  const ws = useRef(null)

  useEffect(() => {
    connect()

    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  const connect = () => {
    try {
      ws.current = new WebSocket(WS_URL)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        setConnected(true)
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        setConnected(false)
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          connect()
        }, 5000)
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
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
