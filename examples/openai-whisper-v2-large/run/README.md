# Whisper Large v2
The Whisper model is intrinsically designed to work on audio samples of up to 30s in duration. 

Using a chunking algorithm through the Transformers pipeline method, it can be used to transcribe audio samples of up to arbitrary length.

This version of OpenAI's Whisper model allows for long-form transcription.

By passing in `return_timestamps=True` to the pipeline, the model will return timestamps alongside the transcription.
