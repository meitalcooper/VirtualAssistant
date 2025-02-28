"""
Whisper Transcription Module

Whisper documentation: https://openai.com/research/whisper


This module processes audio recordings from Twilio calls using OpenAI's Whisper model.
It transcribes spoken content into text and performs cleaning operations to standardize
user-provided data.

Features:
- Converts decrypted audio recordings into text using Whisper's ASR capabilities.
- Uses Librosa for audio preprocessing and Whisper's log-mel spectrogram for feature extraction.
- Implements error handling to ensure robustness against malformed or empty audio input.
- Provides helper functions to clean and normalize user data (e.g., removing spaces, hyphens, and periods from names).
- Integrates with the IVR system to facilitate automated authentication and troubleshooting processes.
"""

import io
import librosa
import whisper
import logging
import re

model = whisper.load_model("turbo")

def transcribe_audio_content(audio_content):
    """Process decrypted audio content with Whisper"""
    try:
        print("\n=== Starting Whisper Transcription ===")
        print(f"Audio content length: {len(audio_content)} bytes")
        
        # Convert audio bytes to format Whisper expects
        audio_data = io.BytesIO(audio_content)
        
        print("Loading audio with librosa...")
        logging.getLogger('numba').setLevel(logging.WARNING)
        samples, sr = librosa.load(audio_data, sr=16000)
        print(f"Loaded audio: {len(samples)} samples at {sr}Hz")
        
        if len(samples) == 0:
            print("Warning: Empty audio samples")
            return None
            
        samples = whisper.pad_or_trim(samples)
        mel = whisper.log_mel_spectrogram(samples, n_mels=model.dims.n_mels).to(model.device)
        
        # Transcribe
        print("Starting whisper transcription...")
        options = whisper.DecodingOptions(
            language="en",
            fp16=False  # Added for compatibility
        )
        transcription = whisper.decode(model, mel, options)
        
        print(f"Transcription result: {transcription.text}")
        return transcription.text.strip()
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full error details: {str(e)}")
        return None

def clean_username(name):
    # Remove spaces, hyphens and periods
    if name:
        cleaned_name = re.sub(r'[ .-]', '', name)
        # Convert to lowercase
        cleaned_name = cleaned_name.lower()
        return cleaned_name
    return None

def clean_manager_name(name):
    # Remove periods and hyphens
    if name:
        cleaned_manager_name = re.sub(r'[.-]', '', name)
        return cleaned_manager_name
    return None
