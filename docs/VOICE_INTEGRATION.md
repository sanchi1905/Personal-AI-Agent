# Voice Integration Guide

## Overview

Phase 6 adds ElevenLabs Conversational AI integration for hands-free voice control of the Personal AI Agent.

## Architecture

### Backend Components

**1. Voice Service** (`src/services/voice_service.py`)
- `ElevenLabsVoiceService` class for TTS operations
- Methods:
  - `text_to_speech()` - Convert text to MP3 audio
  - `stream_text_to_speech()` - Real-time audio streaming
  - `get_available_voices()` - List available AI voices
- Environment variables:
  - `ELEVENLABS_API_KEY` - Your ElevenLabs API key
  - `ELEVENLABS_VOICE_ID` - Default voice ID (Sarah)

**2. API Endpoints** (`src/api/main.py`)
- `POST /api/voice/tts` - Text-to-speech conversion
  ```json
  {
    "text": "Hello, how can I help?",
    "voice_id": "EXAVITQu4vr4xnSDxMaL",
    "model_id": "eleven_monolingual_v1",
    "stability": 0.5,
    "similarity_boost": 0.75
  }
  ```
- `GET /api/voice/voices` - List available voices

### Frontend Components

**1. Voice Service** (`ui/src/services/voiceService.js`)
- Browser-based voice service using Web Speech API
- Features:
  - Speech-to-text (STT) using `SpeechRecognition`
  - Text-to-speech (TTS) via backend API
  - Fallback browser TTS using `SpeechSynthesis`
  - Interim transcript support
  - Voice availability detection

**2. VoiceInput Component** (`ui/src/components/VoiceInput.jsx`)
- Microphone button with visual feedback
- Animated pulse effect when listening
- Interim transcript tooltip display
- Error handling and user feedback

**3. ChatInterface Updates** (`ui/src/components/ChatInterface.jsx`)
- Voice toggle button (speaker icon)
- Automatic TTS for agent responses when enabled
- Integrated VoiceInput component
- Speaking status indicator

## Setup Instructions

### 1. Get ElevenLabs API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to **Profile** → **API Keys**
3. Create a new API key
4. Copy the key

### 2. Configure Environment

Create or update `.env` file:

```bash
# Voice Integration
ELEVENLABS_API_KEY=sk_your_api_key_here
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Sarah (default)
```

### 3. Choose Your Voice (Optional)

1. Visit [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Preview voices and find one you like
3. Copy the Voice ID
4. Update `ELEVENLABS_VOICE_ID` in your `.env`

**Popular Voice IDs:**
- Sarah (Female, Professional): `EXAVITQu4vr4xnSDxMaL`
- Adam (Male, Deep): `pNInz6obpgDQGcFmaJgB`
- Antoni (Male, Well-rounded): `ErXwobaYiN019PkySvjV`
- Bella (Female, Soft): `EXAVITQu4vr4xnSDxMaL`

### 4. Restart Backend

If backend is already running:
```bash
# It should auto-reload with --reload flag
# But if not, restart manually:
Ctrl+C
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### Voice Input (Speech-to-Text)

1. Click the **microphone button** in the chat interface
2. Speak your command clearly
3. You'll see interim transcription in real-time
4. Click again to stop or wait for automatic completion
5. Command sends automatically when you finish speaking

**Example Commands:**
- "Show me disk usage"
- "Check running services"
- "Install Python package requests"
- "Create a backup of my documents"

### Voice Output (Text-to-Speech)

1. Click the **speaker button** to enable voice responses
2. Agent explanations will be read aloud
3. Click again to disable voice responses
4. Speaking indicator shows when audio is playing

### Keyboard Shortcuts

- `Enter` - Send message (with or without voice)
- `Esc` - Stop voice recording
- No keyboard shortcut for voice toggle (use button)

## Technical Details

### Web Speech API Support

| Browser | Speech Recognition | Speech Synthesis |
|---------|-------------------|------------------|
| Chrome  | ✅ Full support   | ✅ Full support  |
| Edge    | ✅ Full support   | ✅ Full support  |
| Opera   | ✅ Full support   | ✅ Full support  |
| Firefox | ⚠️ Limited        | ✅ Full support  |
| Safari  | ⚠️ Limited        | ✅ Full support  |

**Recommendation:** Use Chrome, Edge, or Opera for best experience.

### API Rate Limits

ElevenLabs free tier includes:
- 10,000 characters/month
- 3 custom voices
- All voice library voices

Paid tiers offer:
- Higher character limits
- Voice cloning
- Priority processing
- Commercial usage rights

### Security Considerations

**API Key Protection:**
- ✅ API key stored in `.env` (not committed to git)
- ✅ Backend-only API calls (frontend never sees key)
- ✅ Environment variables loaded at runtime

**Privacy:**
- ⚠️ Voice data sent to ElevenLabs for TTS processing
- ⚠️ Browser speech recognition may use cloud services
- ✅ No voice recordings stored permanently
- ✅ Fallback to browser TTS (fully local) available

**Recommendations:**
- Use browser TTS fallback for sensitive environments
- Review [ElevenLabs Privacy Policy](https://elevenlabs.io/privacy)
- Consider self-hosted TTS for maximum privacy

## Troubleshooting

### Microphone Not Working

**Symptoms:** No voice input detected

**Solutions:**
1. Check browser permissions (lock icon in address bar)
2. Grant microphone access when prompted
3. Verify microphone is not muted in system settings
4. Try different browser (Chrome recommended)
5. Check browser console for errors

### Voice Responses Not Playing

**Symptoms:** No audio output

**Solutions:**
1. Verify `ELEVENLABS_API_KEY` is set in `.env`
2. Check backend console for API errors
3. Test with browser fallback TTS
4. Verify speakers/headphones are working
5. Check browser console for errors

### Transcription Inaccurate

**Symptoms:** Wrong words transcribed

**Solutions:**
1. Speak clearly and at moderate pace
2. Reduce background noise
3. Use quality microphone
4. Check browser language settings
5. Ensure microphone sensitivity is appropriate

### API Quota Exceeded

**Symptoms:** "Quota exceeded" error

**Solutions:**
1. Check ElevenLabs dashboard for usage
2. Upgrade to paid plan
3. Use browser fallback TTS (unlimited)
4. Reduce voice response frequency

### Backend Connection Failed

**Symptoms:** "Failed to fetch" errors

**Solutions:**
1. Verify backend is running on port 8000
2. Check CORS configuration
3. Verify network connectivity
4. Check backend console for errors

## Code Examples

### Using Voice Service Directly

```python
from src.services.voice_service import ElevenLabsVoiceService

# Initialize
voice = ElevenLabsVoiceService()

# Text to speech
audio_bytes = voice.text_to_speech(
    "Hello, I am your AI assistant",
    voice_id="EXAVITQu4vr4xnSDxMaL"
)

# Save to file
with open("response.mp3", "wb") as f:
    f.write(audio_bytes)

# Get available voices
voices = voice.get_available_voices()
for v in voices:
    print(f"{v['name']}: {v['voice_id']}")
```

### Frontend Voice Integration

```javascript
import { voiceService } from '../services/voiceService';

// Start listening
voiceService.startListening(
  (transcript) => {
    console.log("Interim:", transcript);
  },
  (transcript) => {
    console.log("Final:", transcript);
    // Send command
  },
  (error) => {
    console.error("Error:", error);
  }
);

// Speak text
await voiceService.speak("Your command executed successfully");

// Stop listening
voiceService.stopListening();
```

## Performance Optimization

### Reduce Latency

1. **Use Streaming TTS** (future enhancement):
   ```python
   for chunk in voice.stream_text_to_speech(long_text):
       # Play chunk immediately
       pass
   ```

2. **Cache Common Responses**:
   ```python
   # Pre-generate common phrases
   common_phrases = {
       "success": voice.text_to_speech("Command executed successfully"),
       "error": voice.text_to_speech("An error occurred"),
   }
   ```

3. **Adjust Voice Settings**:
   ```python
   # Faster generation (lower quality)
   audio = voice.text_to_speech(
       text,
       model_id="eleven_turbo_v2",  # Faster model
       stability=0.3  # Lower stability = faster
   )
   ```

### Reduce Costs

1. **Selective Voice Responses**:
   - Only enable for important messages
   - User controls when to hear responses

2. **Use Browser TTS Fallback**:
   - Free and unlimited
   - Lower quality but acceptable

3. **Summarize Long Responses**:
   ```python
   if len(response) > 500:
       summary = summarize(response)
       audio = voice.text_to_speech(summary)
   ```

## Future Enhancements

### Planned Features

1. **Voice Commands Library**
   - Pre-defined voice shortcuts
   - Custom voice macros
   - Voice command history

2. **Multi-language Support**
   - Detect user language
   - Translate responses
   - Multi-lingual voices

3. **Voice Cloning**
   - Clone user's voice
   - Personalized responses
   - Custom voice personas

4. **Conversation Mode**
   - Continuous listening
   - Natural dialogue flow
   - Context-aware responses

5. **Offline Voice Support**
   - Local TTS models (Piper, Coqui)
   - Offline STT (Whisper)
   - No internet required

6. **Voice Analytics**
   - Usage statistics
   - Command patterns
   - Voice preference learning

## Resources

- [ElevenLabs Documentation](https://docs.elevenlabs.io/)
- [Web Speech API Docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Voice Library](https://elevenlabs.io/voice-library)
- [ElevenLabs Pricing](https://elevenlabs.io/pricing)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review browser console errors
3. Check backend logs
4. File issue on GitHub

---

**Phase 6 Voice Integration** - Making AI assistance more natural and accessible through voice interaction.
