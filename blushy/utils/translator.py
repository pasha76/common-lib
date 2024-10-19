from beam import env
from transformers import MarianMTModel, MarianTokenizer

PATH= "/users/tolgagunduz/downloads/"

if env.is_remote():
    PATH= "/volumes/model-weights/model-weigths/"


def translate_to_english(text):


    model_name = f'Helsinki-NLP/opus-mt-tr-en'

    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name,cache_dir=PATH)
        model = MarianMTModel.from_pretrained(model_name,cache_dir=PATH)
    except Exception:
        return f"No available model for translating from 'tr' to English."

    # Tokenize and translate
    batch = tokenizer([text], return_tensors="pt", padding=True)
    generated_ids = model.generate(**batch)
    translated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    return translated_text