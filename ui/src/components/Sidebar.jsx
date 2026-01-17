import { 
  ChartBarIcon, 
  Cog6ToothIcon, 
  DocumentTextIcon,
  CubeIcon,
  ServerIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

export default function Sidebar({ activeView, onViewChange, systemStatus }) {
  const menuItems = [
    { id: 'status', label: 'System Status', icon: ChartBarIcon },
    { id: 'apps', label: 'Applications', icon: CubeIcon },
    { id: 'services', label: 'Services', icon: ServerIcon },
    { id: 'logs', label: 'Activity Log', icon: DocumentTextIcon },
    { id: 'history', label: 'History', icon: ClockIcon },
    { id: 'settings', label: 'Settings', icon: Cog6ToothIcon },
  ]

  return (
    <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Logo/Title */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <div>
            <h2 className="text-white font-bold">AI Agent</h2>
            <p className="text-xs text-slate-400">Desktop UI</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeView === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Footer - Quick Stats */}
      {systemStatus && (
        <div className="p-4 border-t border-slate-700 space-y-2">
          <div className="text-xs text-slate-400">Quick Stats</div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">CPU</span>
              <span className="text-slate-300">{systemStatus.cpu_percent.toFixed(0)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">Memory</span>
              <span className="text-slate-300">{systemStatus.memory_percent.toFixed(0)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">Disk</span>
              <span className="text-slate-300">{systemStatus.disk_percent.toFixed(0)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
