# 🔧 Orpheus TTS Fix Report

## Problem Summary

The Orpheus TTS integration was generating **unusual audio** containing "date check" and other strange text instead of the expected speech. The generated audio was also much longer than expected for short phrases.

## Root Cause Analysis

### Primary Issue: Wrong API Endpoint
The application was using **`/chat/completions`** (Chat Completion API) instead of **`/completions`** (Text Completion API).

- ❌ **Before**: Using OpenAI's `chat.completions.create()` which maps to `/chat/completions`
- ✅ **After**: Using `httpx` to directly call `/completions` endpoint

### Secondary Issue: No Streaming
LM Studio was not returning the special `<custom_token_XXX>` tags because:
1. We weren't using the streaming API
2. The prompt format was incorrect
3. LM Studio was treating Orpheus as a regular text LLM

## What Was Fixed

### 1. API Endpoint Change
```python
# BEFORE (❌ Wrong)
response = await self.client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": prompt}],
    ...
)

# AFTER (✅ Correct)
async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        f"{self.base_url}/completions",
        json={
            "model": "local-model",
            "prompt": prompt,
            "stream": True,  # Essential!
            ...
        },
        ...
    ) as response:
```

### 2. Prompt Format
```python
# BEFORE (❌ Wrong)
return f"<|im_start|>{self.voice}\n{text}<|im_end|>"

# AFTER (✅ Correct - from reference repo)
return f"<|audio|>{self.voice}: {text}<|eot_id|>"
```

### 3. Parameter Name
```python
# BEFORE (❌ Wrong)
"repetition_penalty": self.repetition_penalty

# AFTER (✅ Correct)
"repeat_penalty": self.repetition_penalty
```

### 4. Streaming Token Processing
Now we process tokens as they arrive in real-time:
```python
async for line in response.aiter_lines():
    if line.startswith("data: "):
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            break
        
        data = json.loads(data_str)
        token_text = data["choices"][0].get("text", "")
        
        # Extract custom tokens
        token_matches = re.findall(r'<custom_token_(\d+)>', token_text)
        # Process tokens...
```

## Files Modified

1. **`src/voiceagent/models/orpheus_tts.py`**
   - Changed from `AsyncOpenAI` to `httpx` for direct API control
   - Updated `_format_prompt()` to use correct Orpheus format
   - Rewrote `run()` method to use streaming `/completions` endpoint
   - Removed duplicate token processing code

2. **`pyproject.toml`**
   - Added `httpx>=0.27.0` dependency
   - Ensured `torch`, `snac`, and other SNAC dependencies are included

## Test Results

### Before Fix
```
⚠ No <custom_token_XXX> tags found in response
✗ No audio generated
```

LM Studio was returning regular text like: *"tara: Let me just say… I've never wanted to be a part of a rock band..."*

### After Fix
```
✓ Extracted 273 tokens, generated 36 audio chunks
✓ Audio saved to: generated_audio/orpheus_tts_1.wav
✓ Speech synthesized (147500 bytes)

✓ Extracted 1085 tokens, generated 152 audio chunks
✓ Audio saved to: generated_audio/orpheus_tts_2.wav
✓ Speech synthesized (622636 bytes)
```

### Audio Quality Verification
```
File: orpheus_tts_2.wav
  Duration: 12.97 seconds
  Sample rate: 24000 Hz
  Max amplitude: 0.4400
  ✓ Audio has proper amplitude
  ✓ Audio duration looks reasonable
```

## Why This Matters

### OpenAI Agents SDK Compatibility
The OpenAI Agents SDK's `TTSModel` interface expects:
- A `run()` method that returns `AsyncIterator[bytes]`
- PCM audio data
- Works with any TTS model

However, Orpheus TTS has specific requirements:
- **Must** use `/completions` endpoint (not `/chat/completions`)
- **Must** enable streaming (`"stream": True`)
- **Must** use correct prompt format (`<|audio|>` tokens)
- Outputs custom tokens that need SNAC decoding

Our fix bridges this gap by:
1. Using `httpx` for direct API control
2. Processing streamed custom tokens
3. Converting tokens to PCM audio via SNAC decoder
4. Yielding chunks compatible with OpenAI Agents SDK

## Reference Implementation

Based on: [isaiahbjork/orpheus-tts-local](https://github.com/isaiahbjork/orpheus-tts-local)

Key insights from reference repo:
- Uses `requests.post()` with `stream=True`
- Calls `/completions` endpoint directly
- Processes SSE (Server-Sent Events) format: `data: {...}\n\n`
- Extracts `<custom_token_XXX>` from streamed text
- Uses SNAC decoder to convert tokens to audio

## How to Verify

1. **Start LM Studio**
   - Load `lex-au/Orpheus-3b-FT-Q4_K_M.gguf`
   - Start local server on `http://localhost:1234`

2. **Run the application**
   ```bash
   python main.py
   ```

3. **Select Option 2** (Text Chat with Voice Response)

4. **Type a message** and listen to the audio

5. **Check generated files**
   ```bash
   ls -lh generated_audio/
   # Should see .wav files with reasonable sizes (100-600 KB)
   ```

## Summary

✅ **FIXED**: Orpheus TTS now correctly:
- Uses `/completions` endpoint with streaming
- Extracts custom tokens from LM Studio
- Decodes tokens using SNAC
- Generates proper audio speech
- Works seamlessly with OpenAI Agents SDK

The audio should now contain **only the spoken response**, without any strange "date check" or other extraneous text.

---

*Last updated: 2026-01-10*
*Issue: Strange audio generation with extra content*
*Solution: Use correct API endpoint (/completions) with streaming*



