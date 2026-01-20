import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Voice Service - ElevenLabs Integration
 * 
 * Handles voice input/output using browser APIs and ElevenLabs
 */

class VoiceService {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.audioContext = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
  }

  /**
   * Initialize speech recognition
   */
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser');
      return false;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
    
    return true;
  }

  /**
   * Start listening for voice input
   * @param {Function} onResult - Callback for interim results
   * @param {Function} onFinal - Callback for final result
   * @param {Function} onError - Callback for errors
   */
  startListening(onResult, onFinal, onError) {
    if (!this.recognition && !this.initSpeechRecognition()) {
      onError?.(new Error('Speech recognition not available'));
      return;
    }

    this.isListening = true;

    this.recognition.onresult = (event) => {
      const results = Array.from(event.results);
      const transcript = results
        .map(result => result[0].transcript)
        .join('');

      if (event.results[event.results.length - 1].isFinal) {
        onFinal?.(transcript);
      } else {
        onResult?.(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.isListening = false;
      const errorMessage = event.error === 'not-allowed' 
        ? 'Microphone access denied. Please allow microphone permissions.'
        : event.error === 'no-speech'
        ? 'No speech detected. Please try again.'
        : `Voice recognition error: ${event.error}`;
      onError?.({ message: errorMessage, code: event.error });
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };

    try {
      this.recognition.start();
    } catch (error) {
      console.error('Failed to start recognition:', error);
      this.isListening = false;
      onError?.(error);
    }
  }

  /**
   * Stop listening
   */
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }

  /**
   * Check if voice features are available
   */
  isVoiceAvailable() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    return {
      recognition: !!SpeechRecognition,
      synthesis: !!window.speechSynthesis
    };
  }

  /**
   * Text-to-speech using ElevenLabs API
   * @param {string} text - Text to speak
   * @param {Object} options - Voice options
   */
  async speak(text, options = {}) {
    try {
      const response = await axios.post(`${API_BASE_URL}/voice/tts`, {
        text,
        voice_id: options.voiceId || null,
        settings: {
          stability: options.stability || 0.5,
          similarity_boost: options.similarityBoost || 0.75
        }
      }, {
        responseType: 'blob'
      });

      // Create audio from blob
      const audioBlob = response.data;
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          resolve();
        };
        audio.onerror = (error) => {
          URL.revokeObjectURL(audioUrl);
          reject(error);
        };
        audio.play();
      });
    } catch (error) {
      console.error('TTS error:', error);
      // Fallback to browser TTS
      return this.speakWithBrowserTTS(text);
    }
  }

  /**
   * Fallback: Browser text-to-speech
   * @param {string} text - Text to speak
   */
  speakWithBrowserTTS(text) {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      utterance.onend = resolve;
      utterance.onerror = reject;

      this.synthesis.speak(utterance);
    });
  }

  /**
   * Stop current speech
   */
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  /**
   * Get available voices from ElevenLabs
   */
  async getAvailableVoices() {
    try {
      const response = await axios.get(`${API_BASE_URL}/voice/voices`);
      return response.data.voices || [];
    } catch (error) {
      console.error('Failed to get voices:', error);
      return [];
    }
  }

  /**
   * Check if voice features are available
   */
  isVoiceAvailable() {
    return {
      recognition: 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window,
      synthesis: 'speechSynthesis' in window,
      mediaRecorder: 'MediaRecorder' in window
    };
  }
}

export default new VoiceService();
