"""
Audio transcription using Gemini 2.5 Flash
Supports microphone recording via Streamlit
"""
from google import genai
import tempfile
import os
from config import GEMINI_API_KEY

# Initialize Gemini client
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not configured")
client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribe audio bytes using Gemini 2.5 Flash
    
    Args:
        audio_bytes: Audio data as bytes
        mime_type: MIME type of audio (default: "audio/webm" for browser recordings)
    
    Returns:
        Transcribed text
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured. Please set GEMINI_API_KEY in your .env file.")
    
    try:
        # Save audio bytes temporarily
        suffix = ".webm"  # Default for browser recordings
        if mime_type:
            if "wav" in mime_type:
                suffix = ".wav"
            elif "mp3" in mime_type:
                suffix = ".mp3"
            elif "ogg" in mime_type:
                suffix = ".ogg"
            elif "flac" in mime_type:
                suffix = ".flac"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Create prompt for transcription
            prompt = "Please transcribe this audio file word for word. Return only the transcribed text, nothing else. Do not add any explanations or formatting."
            
            # Generate transcription using Gemini 2.5 Flash
            model_name = "models/gemini-2.5-flash"
            
            # Try different methods to pass audio to Gemini
            response = None
            last_error = None
            
            # Method 1: Try using types.Part.from_bytes (new API)
            try:
                from google.genai import types
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        prompt,
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type=mime_type
                        )
                    ]
                )
            except Exception as e1:
                last_error = str(e1)
                # Method 2: Try passing file path as string
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[prompt, tmp_path]
                    )
                except Exception as e2:
                    last_error = str(e2)
                    # Method 3: Try reading file and creating Part object
                    try:
                        from google.genai import types
                        with open(tmp_path, 'rb') as f:
                            file_bytes = f.read()
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[
                                prompt,
                                types.Part.from_bytes(
                                    data=file_bytes,
                                    mime_type=mime_type
                                )
                            ]
                        )
                    except Exception as e3:
                        last_error = str(e3)
                        raise Exception(f"All transcription methods failed. Last error: {last_error}")
            
            if response is None:
                raise Exception(f"Failed to get response. Last error: {last_error}")
            
            transcript = (getattr(response, "text", "") or "").strip()
            if not transcript:
                raise Exception("Gemini returned empty transcript")
            
            return transcript
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
                
    except Exception as e:
        raise Exception(f"Error transcribing audio with Gemini: {str(e)}")

