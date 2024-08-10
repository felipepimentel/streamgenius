from transformers import MarianMTModel, MarianTokenizer

def translate(text: str, target_lang: str = "pt"):
    """
    Translate text to target language (default: Portuguese).
    """
    model_name = f'Helsinki-NLP/opus-mt-en-{target_lang}'
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    # Tokenize the text
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    
    # Decode the generated tokens
    translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    
    return translated_text[0]
