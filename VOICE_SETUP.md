# 🎙️ Voice Integration Setup Guide

## Current Status

✅ **Backend Server**: Running on http://localhost:8000  
✅ **Frontend Server**: Running on http://localhost:3000  
⚠️ **Voice Service**: Disabled (missing API key)

---

## Quick Fix: Get Your Voice Features Working

### Option 1: Use ElevenLabs (Recommended - Best Quality)

**Step 1: Get API Key**
1. Go to https://elevenlabs.io/
2. Sign up for a free account
3. Navigate to **Profile** → **API Keys**
4. Click "Create New API Key"
5. Copy the API key

**Step 2: Add to .env File**
1. Open `.env` file in your project root
2. Find this line:
   ```
   ELEVENLABS_API_KEY=
   ```
3. Paste your API key:
   ```
   ELEVENLABS_API_KEY=sk_your_actual_api_key_here
   ```
4. Save the file

**Step 3: Restart Backend**
- The backend will auto-reload when you save `.env`
- Or manually restart: Press Ctrl+C in backend terminal, then run:
  ```powershell
  cd "c:\Users\Asus\Downloads\Personal AI Agent\personal-ai-agent"
  python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
  ```

**Step 4: Test Voice Features**
1. Open http://localhost:3000
2. Click the **microphone button** (🎤) in the chat
3. Speak: "Show me disk usage"
4. Click the **speaker button** (🔊) to enable voice responses

---

### Option 2: Use Browser TTS (Free - No API Key Needed)

The app includes a **fallback mode** using your browser's built-in text-to-speech:

**Advantages:**
- ✅ Completely free
- ✅ Works offline
- ✅ No API key required
- ✅ Unlimited usage

**Disadvantages:**
- ⚠️ Lower voice quality
- ⚠️ Robotic sound
- ⚠️ Limited voice options

**How to Use:**
1. Open http://localhost:3000
2. Click the **speaker button** to enable voice responses
3. When API key is missing, browser TTS activates automatically
4. Voice input (microphone) works without API key!

---

## What's Working Right Now

### ✅ Voice Input (Speech-to-Text)
- **Status**: Fully working (no API key needed)
- **Browser Support**: Chrome, Edge, Opera (best)
- **How to Use**: Click microphone button and speak

### ⚠️ Voice Output (Text-to-Speech)
- **ElevenLabs**: Disabled (needs API key)
- **Browser Fallback**: Working (automatic)
- **How to Use**: Click speaker button to toggle

---

## Troubleshooting

### "Microphone button is grayed out"
**Cause**: Browser doesn't support Web Speech API  
**Solution**: Use Chrome, Edge, or Opera browser

### "No voice output when clicking speaker"
**Cause**: ElevenLabs API key missing  
**Solution**:  
- Add API key (Option 1 above), OR
- Use browser fallback (already working)

### "Backend shows warning about API key"
**Expected Behavior**: This is normal if you haven't added your API key yet  
**Impact**: Voice features use browser fallback instead  
**Solution**: Add API key to remove warning and get high-quality voices

### "Voice input stops immediately"
**Cause**: Microphone permissions not granted  
**Solution**:  
1. Click the lock icon in browser address bar
2. Grant microphone permissions
3. Refresh the page
4. Try again

---

## ElevenLabs Free Tier Limits

- **Characters/Month**: 10,000 (about 15-20 minutes of speech)
- **Voices Available**: All voice library voices
- **Custom Voices**: 3 custom voice clones
- **Cost**: $0.00

**Estimated Usage:**
- Short command responses: ~50-100 characters each
- 10,000 characters = ~100-200 responses per month
- Perfect for testing and moderate use

---

## Testing Your Setup

### Test 1: Voice Input (No API Key Needed)
1. Open http://localhost:3000
2. Click microphone button (should turn red and pulse)
3. Say: "List files in current directory"
4. You should see interim transcript appear
5. Command should execute automatically

**Expected**: ✅ Works immediately

### Test 2: Voice Output with Browser TTS
1. Click speaker button (should show "Voice On")
2. Type a command: "Check disk space"
3. Agent response should be read aloud (robotic voice)

**Expected**: ✅ Works with browser voice

### Test 3: Voice Output with ElevenLabs
1. Add API key to `.env` file
2. Restart backend
3. Click speaker button  
4. Type a command
5. Agent response should be read aloud (natural voice)

**Expected**: ✅ High-quality natural voice

---

## API Key Configuration File Location

**File**: `c:\Users\Asus\Downloads\Personal AI Agent\personal-ai-agent\.env`

**Required Lines:**
```bash
# Voice Integration (ElevenLabs)
ELEVENLABS_API_KEY=sk_your_api_key_here
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
```

**After editing**: Backend auto-reloads (watch terminal for "Application startup complete")

---

## Voice Selection (After API Key is Added)

**Default Voice**: Sarah (`EXAVITQu4vr4xnSDxMaL`)

**Popular Alternatives:**
- **Adam** (Male, Deep): `pNInz6obpgDQGcFmaJgB`
- **Antoni** (Male, Well-rounded): `ErXwobaYiN019PkySvjV`
- **Rachel** (Female, Calm): `21m00Tcm4TlvDq8ikWAM`
- **Josh** (Male, Energetic): `TxGEqnHWrfWFTfGW9XjX`

**To Change Voice:**
1. Open `.env`
2. Update `ELEVENLABS_VOICE_ID=` with new voice ID
3. Save file (backend auto-reloads)

---

## Next Steps

### 1. Get Voice Working (Choose One)
- [ ] **Easy**: Use browser TTS (already working, click speaker button)
- [ ] **Better**: Add ElevenLabs API key (5 minutes setup)

### 2. Test Features
- [ ] Test voice input (microphone button)
- [ ] Test voice output (speaker button)
- [ ] Try different commands
- [ ] Adjust voice if using ElevenLabs

### 3. Optional Enhancements
- [ ] Try different voices from ElevenLabs library
- [ ] Adjust voice settings (stability, similarity)
- [ ] Monitor API usage in ElevenLabs dashboard

---

## Quick Reference

| Feature | Status | Requirements |
|---------|--------|--------------|
| Voice Input (STT) | ✅ Working | Modern browser only |
| Voice Output (Browser) | ✅ Working | None |
| Voice Output (ElevenLabs) | ⚠️ Needs API key | Free API key |
| Backend Server | ✅ Running | Port 8000 |
| Frontend UI | ✅ Running | Port 3000 |

---

## Support

**Issue**: Voice features not working?  
**Check**:
1. Is backend running? → Check http://localhost:8000
2. Is frontend running? → Check http://localhost:3000
3. Browser compatibility? → Use Chrome/Edge
4. Microphone permissions? → Check browser settings
5. API key added? → Check `.env` file

**Still having issues?**
- Check browser console (F12) for errors
- Check backend terminal for error messages
- Verify `.env` file has no typos
- Try refreshing the page

---

## Summary

🎯 **What You Need to Do:**

1. **For Basic Voice** (Working Now):
   - Just use browser TTS fallback
   - Click speaker button to enable
   
2. **For Better Voice** (5 min setup):
   - Get free ElevenLabs API key
   - Add to `.env` file
   - Restart backend

Both voice input and basic voice output work **right now** without any API key! 🎉
