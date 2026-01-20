import { ExclamationTriangleIcon, ShieldCheckIcon, XMarkIcon, CheckIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'

export default function CommandPreview({ command, onConfirm, onCancel }) {
  const [executing, setExecuting] = useState(false)

  const handleConfirm = () => {
    console.log('[CommandPreview] Confirm button clicked')
    onConfirm()
  }

  return (
    <div className="h-full flex flex-col p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Command Preview</h2>
        <button
          onClick={onCancel}
          className="text-slate-400 hover:text-white transition-colors"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto">
        {/* Command */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Command</label>
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-3">
            <code className="text-sm text-cyan-400 font-mono break-all">
              {command.command}
            </code>
          </div>
        </div>

        {/* Explanation */}
        {command.explanation && (
          <div>
            <label className="text-xs text-slate-400 mb-2 block">What this does</label>
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-3">
              <p className="text-sm text-slate-200">{command.explanation}</p>
            </div>
          </div>
        )}

        {/* Safety Status */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Safety Status</label>
          <div className={`rounded-lg p-3 ${
            command.is_safe 
              ? 'bg-green-500/10 border border-green-500/50' 
              : 'bg-red-500/10 border border-red-500/50'
          }`}>
            <div className="flex items-center space-x-2">
              {command.is_safe ? (
                <>
                  <ShieldCheckIcon className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-green-400 font-medium">Safe to execute</span>
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
                  <span className="text-sm text-red-400 font-medium">Proceed with caution</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Risks & Warnings */}
        {command.risks && command.risks.length > 0 && (
          <div>
            <label className="text-xs text-slate-400 mb-2 block">Warnings</label>
            <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-3">
              <ul className="space-y-2">
                {command.risks.map((risk, index) => (
                  <li key={index} className="text-sm text-yellow-400 flex items-start space-x-2">
                    <span className="mt-0.5">⚠️</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Optimizations */}
        {command.optimizations && command.optimizations.length > 0 && (
          <div>
            <label className="text-xs text-slate-400 mb-2 block">Optimization Suggestions</label>
            <div className="bg-blue-500/10 border border-blue-500/50 rounded-lg p-3">
              <ul className="space-y-2">
                {command.optimizations.map((opt, index) => (
                  <li key={index} className="text-sm text-blue-400 flex items-start space-x-2">
                    <span className="mt-0.5">💡</span>
                    <span>{opt}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Admin Required */}
        {command.requires_admin && (
          <div className="bg-purple-500/10 border border-purple-500/50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="w-5 h-5 text-purple-400" />
              <span className="text-sm text-purple-400">Requires administrator privileges</span>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 space-y-3">
        <button
          onClick={handleConfirm}
          disabled={executing}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
        >
          <CheckIcon className="w-5 h-5" />
          <span>Confirm & Execute</span>
        </button>
        
        <button
          onClick={onCancel}
          disabled={executing}
          className="w-full bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-slate-200 py-3 px-4 rounded-lg font-medium transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}
