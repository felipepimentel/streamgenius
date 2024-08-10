from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import torch
import soundfile as sf

def transcribe(audio_file: str):
    """
    Transcribe audio file using Wav2Vec2 model.
    """
    # Load pre-trained model and tokenizer
    tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    # Load audio
    audio_input, _ = sf.read(audio_file)
    
    # Tokenize
    input_values = tokenizer(audio_input, return_tensors="pt").input_values
    
    # Retrieve logits
    logits = model(input_values).logits
    
    # Take argmax and decode
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = tokenizer.batch_decode(predicted_ids)[0]
    
    return transcription
