"""
ElevenLabs Voice Integration Service

Provides speech-to-text and text-to-speech capabilities using
ElevenLabs Conversational AI API.
"""

import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class ElevenLabsVoiceService:
    """
    ElevenLabs Conversational AI integration.
    
    Features:
    - Text-to-speech with natural voices
    - Speech-to-text conversion
    - Real-time voice interaction
    - Multiple voice options
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs service.
        
        Args:
            api_key: ElevenLabs API key (or read from env)
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Default voice settings
        self.default_voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Sarah
        self.model_id = "eleven_monolingual_v1"
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not found. Voice features will be disabled.")
    
    def text_to_speech(self, text: str, 
                       voice_id: Optional[str] = None,
                       **kwargs) -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (optional)
            **kwargs: Additional voice settings
        
        Returns:
            Audio bytes (MP3 format) or None if failed
        """
        if not self.api_key:
            logger.error("Cannot perform TTS: No API key configured")
            return None
        
        voice = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Voice settings
        voice_settings = {
            "stability": kwargs.get('stability', 0.5),
            "similarity_boost": kwargs.get('similarity_boost', 0.75),
            "style": kwargs.get('style', 0.0),
            "use_speaker_boost": kwargs.get('use_speaker_boost', True)
        }
        
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": voice_settings
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"TTS successful: {len(text)} chars -> {len(response.content)} bytes")
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS failed: {e}")
            return None
    
    def get_available_voices(self) -> Optional[list]:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries or None if failed
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            voices = data.get('voices', [])
            
            logger.info(f"Retrieved {len(voices)} available voices")
            return voices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get voices: {e}")
            return None
    
    def get_voice_settings(self, voice_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get current settings for a voice.
        
        Args:
            voice_id: Voice ID to query
        
        Returns:
            Voice settings dictionary or None
        """
        if not self.api_key:
            return None
        
        voice = voice_id or self.default_voice_id
        url = f"{self.base_url}/voices/{voice}/settings"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get voice settings: {e}")
            return None
    
    def stream_text_to_speech(self, text: str,
                             voice_id: Optional[str] = None):
        """
        Stream text-to-speech audio (for real-time playback).
        
        Args:
            text: Text to convert
            voice_id: Voice ID to use
        
        Yields:
            Audio chunks
        """
        if not self.api_key:
            logger.error("Cannot stream TTS: No API key configured")
            return
        
        voice = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{voice}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, 
                                   stream=True, timeout=30)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS streaming failed: {e}")


# Global instance
_voice_service = None

def get_voice_service() -> ElevenLabsVoiceService:
    """Get or create global ElevenLabs voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = ElevenLabsVoiceService()
    return _voice_service
