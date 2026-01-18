import { useState, useEffect } from 'react';
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/solid';
import voiceService from '../services/voiceService';

export default function VoiceInput({ onTranscript, onFinalTranscript }) {
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isAvailable, setIsAvailable] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if voice input is available
    const availability = voiceService.isVoiceAvailable();
    setIsAvailable(availability.recognition);
  }, []);

  const startListening = () => {
    setError(null);
    setInterimTranscript('');
    setIsListening(true);

    voiceService.startListening(
      // On interim result
      (transcript) => {
        setInterimTranscript(transcript);
        onTranscript?.(transcript);
      },
      // On final result
      (transcript) => {
        setIsListening(false);
        setInterimTranscript('');
        onFinalTranscript?.(transcript);
      },
      // On error
      (err) => {
        setIsListening(false);
        setInterimTranscript('');
        setError(err.message || 'Voice recognition failed');
      }
    );
  };

  const stopListening = () => {
    voiceService.stopListening();
    setIsListening(false);
    setInterimTranscript('');
  };

  if (!isAvailable) {
    return (
      <button
        disabled
        className="p-2 text-gray-500 cursor-not-allowed"
        title="Voice input not available in this browser"
      >
        <MicrophoneIcon className="h-5 w-5" />
      </button>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={isListening ? stopListening : startListening}
        className={`p-2 rounded-lg transition-colors ${
          isListening
            ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
        title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? (
          <StopIcon className="h-5 w-5" />
        ) : (
          <MicrophoneIcon className="h-5 w-5" />
        )}
      </button>

      {/* Interim transcript display */}
      {interimTranscript && (
        <div className="absolute bottom-full mb-2 right-0 bg-gray-800 text-white px-3 py-2 rounded-lg shadow-lg max-w-xs">
          <div className="text-xs text-gray-400 mb-1">Listening...</div>
          <div className="text-sm">{interimTranscript}</div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="absolute bottom-full mb-2 right-0 bg-red-500 text-white px-3 py-2 rounded-lg shadow-lg max-w-xs">
          <div className="text-sm">{error}</div>
        </div>
      )}
    </div>
  );
}
