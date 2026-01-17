import { CpuChipIcon, CircleStackIcon, ServerIcon } from '@heroicons/react/24/outline'

export default function SystemStatus({ systemStatus }) {
  if (!systemStatus) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading system status...</p>
        </div>
      </div>
    )
  }

  const getStatusColor = (percent) => {
    if (percent < 60) return 'text-green-400'
    if (percent < 80) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getProgressColor = (percent) => {
    if (percent < 60) return 'bg-green-500'
    if (percent < 80) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="h-full flex flex-col p-6">
      <h2 className="text-lg font-semibold text-white mb-6">System Status</h2>

      <div className="space-y-6">
        {/* CPU */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <CpuChipIcon className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-slate-300">CPU Usage</span>
            </div>
            <span className={`text-sm font-medium ${getStatusColor(systemStatus.cpu_percent)}`}>
              {systemStatus.cpu_percent.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(systemStatus.cpu_percent)}`}
              style={{ width: `${systemStatus.cpu_percent}%` }}
            ></div>
          </div>
        </div>

        {/* Memory */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <CircleStackIcon className="w-5 h-5 text-purple-400" />
              <span className="text-sm text-slate-300">Memory Usage</span>
            </div>
            <span className={`text-sm font-medium ${getStatusColor(systemStatus.memory_percent)}`}>
              {systemStatus.memory_percent.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(systemStatus.memory_percent)}`}
              style={{ width: `${systemStatus.memory_percent}%` }}
            ></div>
          </div>
        </div>

        {/* Disk */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <ServerIcon className="w-5 h-5 text-cyan-400" />
              <span className="text-sm text-slate-300">Disk Usage</span>
            </div>
            <span className={`text-sm font-medium ${getStatusColor(systemStatus.disk_percent)}`}>
              {systemStatus.disk_percent.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(systemStatus.disk_percent)}`}
              style={{ width: `${systemStatus.disk_percent}%` }}
            ></div>
          </div>
        </div>

        {/* Recommendations */}
        {systemStatus.recommendations && systemStatus.recommendations.length > 0 && (
          <div className="mt-6 pt-6 border-t border-slate-700">
            <h3 className="text-sm font-medium text-slate-300 mb-3">Recommendations</h3>
            <div className="space-y-2">
              {systemStatus.recommendations.map((rec, index) => (
                <div key={index} className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                  <p className="text-xs text-yellow-400">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Health Status Badge */}
        <div className="mt-6 pt-6 border-t border-slate-700">
          <div className="text-center">
            <div className={`inline-block px-4 py-2 rounded-lg font-medium ${
              systemStatus.health_status === 'healthy' ? 'bg-green-500/20 text-green-400' :
              systemStatus.health_status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              System Status: {systemStatus.health_status.toUpperCase()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
