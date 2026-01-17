import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import SystemStatus from './components/SystemStatus'
import Sidebar from './components/Sidebar'
import CommandPreview from './components/CommandPreview'
import ConfirmationModal from './components/ConfirmationModal'
import { useWebSocket } from './hooks/useWebSocket'
import api from './services/api'

function App() {
  const [systemStatus, setSystemStatus] = useState(null)
  const [currentCommand, setCurrentCommand] = useState(null)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [sidebarView, setSidebarView] = useState('status')
  
  const { connected, systemUpdate } = useWebSocket()

  useEffect(() => {
    // Fetch initial system status
    fetchSystemStatus()
    
    // Update every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Update from WebSocket
    if (systemUpdate) {
      setSystemStatus(prev => ({
        ...prev,
        cpu_percent: systemUpdate.cpu,
        memory_percent: systemUpdate.memory,
        disk_percent: systemUpdate.disk,
        health_status: systemUpdate.status
      }))
    }
  }, [systemUpdate])

  const fetchSystemStatus = async () => {
    try {
      const status = await api.getSystemStatus()
      setSystemStatus(status)
    } catch (error) {
      console.error('Failed to fetch system status:', error)
    }
  }

  const handleCommandGenerated = (command) => {
    setCurrentCommand(command)
  }

  const handleConfirm = async (dryRun = false) => {
    if (!currentCommand) return
    
    setShowConfirmation(false)
    
    try {
      const result = await api.executeCommand(currentCommand.command, dryRun)
      
      // Refresh system status after execution
      if (!dryRun && result.success) {
        await fetchSystemStatus()
      }
      
      return result
    } catch (error) {
      console.error('Execution failed:', error)
      throw error
    }
  }

  const handleCancel = () => {
    setShowConfirmation(false)
    setCurrentCommand(null)
  }

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <Sidebar 
        activeView={sidebarView}
        onViewChange={setSidebarView}
        systemStatus={systemStatus}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">AI</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Personal AI Agent</h1>
                <p className="text-sm text-slate-400">Phase 5: Desktop UI</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} ${connected ? 'pulse-glow' : ''}`}></div>
                <span className="text-sm text-slate-400">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {/* System Health Badge */}
              {systemStatus && (
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  systemStatus.health_status === 'healthy' ? 'bg-green-500/20 text-green-400' :
                  systemStatus.health_status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {systemStatus.health_status.toUpperCase()}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Interface */}
          <div className="flex-1 flex flex-col">
            <ChatInterface 
              onCommandGenerated={handleCommandGenerated}
              onShowConfirmation={() => setShowConfirmation(true)}
            />
          </div>

          {/* Right Panel - System Status or Command Preview */}
          <div className="w-96 border-l border-slate-700 bg-slate-800">
            {currentCommand ? (
              <CommandPreview 
                command={currentCommand}
                onConfirm={() => setShowConfirmation(true)}
                onCancel={() => setCurrentCommand(null)}
              />
            ) : (
              <SystemStatus systemStatus={systemStatus} />
            )}
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && currentCommand && (
        <ConfirmationModal
          command={currentCommand}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </div>
  )
}

export default App
