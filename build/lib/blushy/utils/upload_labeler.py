from beam import env
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from blushy.utils.base import url_to_pil_image
import xml.etree.ElementTree as ET
import time

# Set device and data type for CPU

PATH= "/Users/tolgagunduz/Documents/projects/blushyv2/model-weigths/moondream-ft-short"

if env.is_remote():
    PATH= "/volumes/model-weights/model-weigths/moondream-ft-short"


 



class Labeler:
    def __init__(self,device="cpu",PATH=PATH):
        print("Loading Moondream model...",PATH)
        DEVICE = device
        DTYPE = torch.float32 if DEVICE == "cpu" else torch.float16
        MD_REVISION = "2024-08-26"
        # Load model with custom code (trusting remote code)
        self.moondream = AutoModelForCausalLM.from_pretrained(
            PATH,
            revision=MD_REVISION,
            trust_remote_code=True,  # Allows loading custom code
            attn_implementation=None,  # Not using Flash Attention on CPU
            torch_dtype=DTYPE,
              device_map={"": DEVICE})
        
        self.tokenizer = AutoTokenizer.from_pretrained("vikhyatk/moondream2",cache_dir=PATH ,revision=MD_REVISION)# Ensure model is in evaluation mode
        self.moondream.eval()

    def _dict_to_sentence(self,product):

        color = ' and '.join(product['color'])
        features = ', '.join(product['features'])
        sentence = (f"The product is {product['clothe_type']} in {color}. "
                    f"This stylish piece features {features}. ")
        return sentence.lower()

    def _image_to_dict(self, image_source):
        description_dict=[]
        try:
            description_dict = self.moondream.answer_question(
                        self.moondream.encode_image(image_source),
                        "Describe.",
                        tokenizer=self.tokenizer,
                        num_beams=1,
                        repetition_penalty=1.2,
                    )
            description_dict=eval(description_dict)
        except Exception as e:
            return []
        return description_dict

    def label(self, image_source):
        if isinstance(image_source, str):
            image_source = url_to_pil_image(image_source)
        product_list = self._image_to_dict(image_source)
        updated_descriptions=[]
        for product in product_list:
            desc=self._dict_to_sentence(product)
            updated_descriptions.append(desc)
        return updated_descriptions
    
    
    def encode(self, image_sources):
        if isinstance(image_sources, str):
            image_sources = url_to_pil_image(image_sources)
        return self.moondream.encode_image(image_sources)

        
