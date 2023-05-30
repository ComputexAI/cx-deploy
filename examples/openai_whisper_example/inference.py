from fastapi import UploadFile, File

# Whisper specific imports
import whisper
import tempfile


class Predictor:
    """Customer defined class for running inference on a model"""

    def __init__(
            self,
            input_params: dict,
            input_file: UploadFile = File(
                None, description="Optional input file.")
    ):
        self.model = whisper.load_model(input_params["model_name"])
        self.audio_file = input_file

    def transcribe(self):
        """transcribe audio file"""
        audio_data = self.audio_file.file.read()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file.close()

            # Transcribe the audio using the temporary file path
            result = self.model.transcribe(temp_audio_file.name)

        return result["text"]

    async def infer(self):
        """Infer audio file"""
        response = self.transcribe()
        return response
