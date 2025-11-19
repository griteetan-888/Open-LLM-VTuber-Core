import base64
import os
try:
    from pydub import AudioSegment
    from pydub.utils import make_chunks
    PYDUB_AVAILABLE = True
except (ImportError, ModuleNotFoundError, OSError) as e:
    PYDUB_AVAILABLE = False
    AudioSegment = None
    make_chunks = None
    import warnings
    warnings.warn(f"pydub not available: {e}. Audio processing will be limited.")
from ..agent.output_types import Actions
from ..agent.output_types import DisplayText


def _get_volume_by_chunks(audio: AudioSegment, chunk_length_ms: int) -> list:
    """
    Calculate the normalized volume (RMS) for each chunk of the audio.

    Parameters:
        audio (AudioSegment): The audio segment to process.
        chunk_length_ms (int): The length of each audio chunk in milliseconds.

    Returns:
        list: Normalized volumes for each chunk.
    """
    if not PYDUB_AVAILABLE:
        return [0.5] * 10  # Return dummy volumes if pydub is not available
    
    chunks = make_chunks(audio, chunk_length_ms)
    volumes = [chunk.rms for chunk in chunks]
    max_volume = max(volumes)
    if max_volume == 0:
        raise ValueError("Audio is empty or all zero.")
    return [volume / max_volume for volume in volumes]


def prepare_audio_payload(
    audio_path: str | None,
    chunk_length_ms: int = 20,
    display_text: DisplayText = None,
    actions: Actions = None,
    forwarded: bool = False,
) -> dict[str, any]:
    """
    Prepares the audio payload for sending to a broadcast endpoint.
    If audio_path is None, returns a payload with audio=None for silent display.

    Parameters:
        audio_path (str | None): The path to the audio file to be processed, or None for silent display
        chunk_length_ms (int): The length of each audio chunk in milliseconds
        display_text (DisplayText, optional): Text to be displayed with the audio
        actions (Actions, optional): Actions associated with the audio

    Returns:
        dict: The audio payload to be sent
    """
    if isinstance(display_text, DisplayText):
        display_text = display_text.to_dict()

    if not audio_path:
        # Return payload for silent display
        return {
            "type": "audio",
            "audio": None,
            "volumes": [],
            "slice_length": chunk_length_ms,
            "display_text": display_text,
            "actions": actions.to_dict() if actions else None,
            "forwarded": forwarded,
        }

    if not PYDUB_AVAILABLE:
        # Fallback: use ffmpeg to convert audio to WAV format
        # Use dummy volumes since we can't analyze audio without pydub
        import subprocess
        import tempfile
        try:
            # Convert audio to WAV using ffmpeg
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            
            # Use ffmpeg to convert to WAV
            subprocess.run(
                ['ffmpeg', '-i', audio_path, '-y', '-f', 'wav', temp_wav.name],
                capture_output=True,
                check=True
            )
            
            # Read converted WAV file
            with open(temp_wav.name, 'rb') as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Clean up temp file
            os.unlink(temp_wav.name)
            
            # Estimate volumes based on file size (rough approximation)
            file_size_kb = len(audio_bytes) / 1024
            num_chunks = max(10, int(file_size_kb / 5))  # Rough estimate
            volumes = [0.5] * num_chunks
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # If ffmpeg fails, try direct file reading as last resort
            try:
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                file_size_kb = len(audio_bytes) / 1024
                num_chunks = max(10, int(file_size_kb / 5))
                volumes = [0.5] * num_chunks
            except Exception as e2:
                raise ValueError(
                    f"Error processing audio file '{audio_path}': ffmpeg failed ({e}), direct read also failed ({e2})"
                )
    else:
        try:
            audio = AudioSegment.from_file(audio_path)
            audio_bytes = audio.export(format="wav").read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            volumes = _get_volume_by_chunks(audio, chunk_length_ms)
        except Exception as e:
            # Fallback to direct file reading if pydub fails
            try:
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                file_size_kb = len(audio_bytes) / 1024
                num_chunks = max(10, int(file_size_kb / 5))
                volumes = [0.5] * num_chunks
            except Exception as e2:
                raise ValueError(
                    f"Error loading or converting generated audio file to wav file '{audio_path}': {e}, fallback also failed: {e2}"
                )

    payload = {
        "type": "audio",
        "audio": audio_base64,
        "volumes": volumes,
        "slice_length": chunk_length_ms,
        "display_text": display_text,
        "actions": actions.to_dict() if actions else None,
        "forwarded": forwarded,
    }

    return payload


# Example usage:
# payload, duration = prepare_audio_payload("path/to/audio.mp3", display_text="Hello", expression_list=[0,1,2])
