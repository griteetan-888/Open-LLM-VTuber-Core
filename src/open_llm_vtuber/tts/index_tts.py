# src/open_llm_vtuber/tts/index_tts.py
import os
import sys
import requests
import json
from pathlib import Path
from loguru import logger
from .tts_interface import TTSInterface
from typing import Optional

# Add the current directory to sys.path for relative imports if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


class TTSEngine(TTSInterface):
    """
    IndexTTS wrapper for Open-LLM-VTuber
    Uses IndexTTS API for high-quality, emotion-controlled text-to-speech
    """

    def __init__(
        self,
        api_url="http://localhost:8000/tts",  # IndexTTS API endpoint
        voice_path="examples/voice_10.wav",  # Reference voice file
        model_path="checkpoints",  # Model directory
        config_path="checkpoints/config.yaml",  # Config file
        use_emo_text=True,  # Enable emotion from text
        emo_alpha=0.6,  # Emotion intensity
        use_random=False,  # Randomness in generation
        file_extension="wav",
        **kwargs
    ):
        """
        Initialize IndexTTS engine
        
        Args:
            api_url (str): IndexTTS API endpoint URL
            voice_path (str): Path to reference voice file
            model_path (str): Path to model directory
            config_path (str): Path to config file
            use_emo_text (bool): Enable emotion extraction from text
            emo_alpha (float): Emotion intensity (0.0-1.0)
            use_random (bool): Enable randomness in generation
            file_extension (str): Output audio format
        """
        self.api_url = api_url
        self.voice_path = voice_path
        self.model_path = model_path
        self.config_path = config_path
        self.use_emo_text = use_emo_text
        self.emo_alpha = emo_alpha
        self.use_random = use_random
        self.file_extension = file_extension.lower()
        
        if self.file_extension not in ["wav", "mp3"]:
            logger.warning(f"Unsupported file extension '{self.file_extension}' for IndexTTS. Defaulting to 'wav'.")
            self.file_extension = "wav"
            
        self.new_audio_dir = "cache"
        self.temp_audio_file = "temp_index_tts"
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)
            
        logger.info(f"IndexTTS engine initialized with voice: {self.voice_path}")

    def _generate_audio_local(self, text: str, outfile: str) -> Optional[str]:
        """
        Local inference path using IndexTTS library (no HTTP server required).
        Requires IndexTTS repo installed in current environment.
        """
        try:
            # Ensure local IndexTTS repo is importable when running from VTuber root
            try:
                from indextts import __version__ as _iv
            except Exception:
                try:
                    root_dir = Path(__file__).resolve().parents[4]
                except Exception:
                    root_dir = Path.cwd()
                # Prefer to infer repo path from config_path/model_path (index-tts/checkpoints/...)
                inferred_repo = None
                try:
                    cfg_path = Path(self.config_path).resolve()
                    # .../index-tts/checkpoints/config.yaml -> repo = parent.parent
                    inferred_repo = cfg_path.parent.parent
                except Exception:
                    pass
                candidates = [
                    inferred_repo,
                    root_dir / "index-tts",
                    Path.cwd() / "index-tts",
                ]
                for c in candidates:
                    if c and c.exists():
                        parent = c  # parent dir that contains package folder 'indextts'
                        if (parent / "indextts").exists() and str(parent) not in sys.path:
                            sys.path.insert(0, str(parent))
                            break

            # Prefer IndexTTS2 if available, otherwise fallback to IndexTTS (v1 API)
            try:
                from indextts.infer_v2 import IndexTTS2 as _IndexTTS
                engine_name = "IndexTTS2"
            except Exception:
                from indextts.infer import IndexTTS as _IndexTTS
                engine_name = "IndexTTS"

            logger.info(f"Using local {engine_name} for synthesis")
            tts = _IndexTTS(
                model_dir=self.model_path,
                cfg_path=self.config_path,
            )

            # Some versions expect 'spk_audio_prompt', others 'ref_audio'
            kwargs = {
                "text": text,
                "output_path": outfile,
                "verbose": False,
            }
            if hasattr(tts, "infer"):
                # IndexTTS2 signature
                if "spk_audio_prompt" in tts.infer.__code__.co_varnames:
                    kwargs["spk_audio_prompt"] = self.voice_path
                elif "ref_audio" in tts.infer.__code__.co_varnames:
                    kwargs["ref_audio"] = self.voice_path
                else:
                    # Fallback common arg
                    kwargs["spk_audio_prompt"] = self.voice_path
                tts.infer(**kwargs)
            else:
                # Older API
                tts.generate(self.voice_path, text, outfile)

            if os.path.exists(outfile):
                return outfile
            logger.error("Local IndexTTS did not produce an output file")
            return None
        except Exception as e:
            logger.error(f"Local IndexTTS error: {e}")
            return None

    def generate_audio(self, text, file_name_no_ext=None):
        """
        Generate speech audio file using IndexTTS
        
        Args:
            text (str): The text to convert to speech
            file_name_no_ext (str): Name of the file without extension
            
        Returns:
            str: Path to the generated audio file, or None if failed
        """
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        
        # Local direct mode if api_url is set to 'local'
        if str(self.api_url).strip().lower() == "local":
            result = self._generate_audio_local(text, file_name)
            return result

        try:
            # Prepare request data
            data = {
                "text": text,
                "voice_path": self.voice_path,
                "model_path": self.model_path,
                "config_path": self.config_path,
                "use_emo_text": self.use_emo_text,
                "emo_alpha": self.emo_alpha,
                "use_random": self.use_random,
                "output_path": file_name
            }
            
            # Send request to IndexTTS API
            response = requests.post(
                self.api_url,
                json=data,
                timeout=120,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Check if the response contains audio data
                if response.headers.get("content-type", "").startswith("audio/"):
                    # Save audio data directly
                    with open(file_name, "wb") as audio_file:
                        audio_file.write(response.content)
                else:
                    # Response might be JSON with file path or status
                    try:
                        result = response.json()
                        if result.get("success") and result.get("audio_path"):
                            # Copy from generated path to our cache
                            import shutil
                            shutil.copy2(result["audio_path"], file_name)
                        else:
                            logger.error(f"IndexTTS API error: {result.get('error', 'Unknown error')}")
                            return None
                    except json.JSONDecodeError:
                        logger.error("Invalid response from IndexTTS API")
                        return None
                        
                logger.info(f"IndexTTS generated audio: {file_name}")
                return file_name
                
            else:
                logger.error(f"IndexTTS API request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"IndexTTS API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"IndexTTS generation error: {e}")
            return None

    def set_emotion(self, emotion_vector=None, emotion_text=None):
        """
        Set emotion parameters for IndexTTS
        
        Args:
            emotion_vector (list): 8-float emotion vector [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
            emotion_text (str): Text describing the emotion
        """
        if emotion_vector:
            self.emotion_vector = emotion_vector
            self.use_emo_text = False
        if emotion_text:
            self.emotion_text = emotion_text
            self.use_emo_text = True
            
    def set_voice(self, voice_path):
        """
        Set reference voice for IndexTTS
        
        Args:
            voice_path (str): Path to reference voice file
        """
        self.voice_path = voice_path
        logger.info(f"IndexTTS voice changed to: {voice_path}")
