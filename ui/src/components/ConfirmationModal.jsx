import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline'

export default function ConfirmationModal({ command, onConfirm, onCancel }) {
  const [executing, setExecuting] = useState(false)
  const [result, setResult] = useState(null)

  const handleExecute = async (dryRun = false) => {
    setExecuting(true)
    setResult(null)

    try {
      const execResult = await onConfirm(dryRun)
      setResult(execResult)
      
      if (!dryRun && execResult.success) {
        // Close modal after successful execution
        setTimeout(() => {
          onCancel()
        }, 2000)
      }
    } catch (error) {
      setResult({
        success: false,
        error: error.message
      })
    } finally {
      setExecuting(false)
    }
  }

  return (
    <Transition appear show={true} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onCancel}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-75" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-slate-800 border border-slate-700 p-6 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title className="text-xl font-semibold text-white flex items-center space-x-2">
                    <ExclamationTriangleIcon className="w-6 h-6 text-yellow-400" />
                    <span>Confirm Execution</span>
                  </Dialog.Title>
                  <button
                    onClick={onCancel}
                    disabled={executing}
                    className="text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                  >
                    <XMarkIcon className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  {/* Command */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Command to Execute
                    </label>
                    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
                      <code className="text-sm text-cyan-400 font-mono break-all">
                        {command.command}
                      </code>
                    </div>
                  </div>

                  {/* Explanation */}
                  {command.explanation && (
                    <div>
                      <label className="text-sm font-medium text-slate-300 mb-2 block">
                        What This Will Do
                      </label>
                      <p className="text-sm text-slate-400">{command.explanation}</p>
                    </div>
                  )}

                  {/* Warnings */}
                  {command.risks && command.risks.length > 0 && (
                    <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4">
                      <p className="text-sm font-medium text-yellow-400 mb-2">⚠️ Warnings:</p>
                      <ul className="space-y-1">
                        {command.risks.map((risk, index) => (
                          <li key={index} className="text-sm text-yellow-300">• {risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Execution Result */}
                  {result && (
                    <div className={`rounded-lg p-4 ${
                      result.success 
                        ? 'bg-green-500/10 border border-green-500/50' 
                        : 'bg-red-500/10 border border-red-500/50'
                    }`}>
                      <p className={`font-medium mb-2 ${
                        result.success ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {result.success ? '✅ Success!' : '❌ Execution Failed'}
                      </p>
                      
                      {result.dry_run && (
                        <div className="text-sm text-slate-300 mb-2">
                          <p className="font-medium mb-1">Dry Run Results:</p>
                          <p>Will execute: {result.will_execute ? 'Yes' : 'No'}</p>
                          <p>Risk level: {result.risk_level}</p>
                          {result.predicted_changes && result.predicted_changes.length > 0 && (
                            <div className="mt-2">
                              <p className="font-medium">Predicted changes:</p>
                              <ul className="list-disc list-inside">
                                {result.predicted_changes.map((change, i) => (
                                  <li key={i}>{change}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {result.output && !result.dry_run && (
                        <div className="mt-2 bg-slate-900 rounded p-2">
                          <pre className="text-xs text-slate-300 whitespace-pre-wrap overflow-auto max-h-40">
                            {result.output}
                          </pre>
                        </div>
                      )}

                      {result.error && (
                        <p className="text-sm text-red-300">{result.error}</p>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-6 flex items-center space-x-3">
                  <button
                    onClick={() => handleExecute(true)}
                    disabled={executing}
                    className="flex-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-slate-700 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
                  >
                    {executing ? 'Simulating...' : '🔍 Dry Run (Simulate)'}
                  </button>
                  
                  <button
                    onClick={() => handleExecute(false)}
                    disabled={executing}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
                  >
                    {executing ? 'Executing...' : '✅ Execute Now'}
                  </button>
                  
                  <button
                    onClick={onCancel}
                    disabled={executing}
                    className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-slate-200 py-3 px-4 rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
