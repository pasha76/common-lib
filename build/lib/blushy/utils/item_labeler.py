from beam import env
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from blushy.utils.base import url_to_pil_image
import xml.etree.ElementTree as ET
import time
import ast
import re
from blushy.utils.chatgpt_util import describe_image_by_chatgpt
# Set device and data    type for CPU

PATH= "/Users/tolgagunduz/Documents/projects/blushyv2/model-weigths/moondream-ft-long"

if env.is_remote():
    PATH= "/volumes/model-weights/model-weigths/moondream-ft-long"


 



class Labeler:
    def __init__(self,device="cpu",PATH=PATH,CHATGPT=True):
        if not CHATGPT:
            
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
        self.CHATGPT=CHATGPT


    def _parse_incomplete_array(self,input_string):
        # Remove newlines and extra spaces
        input_string = re.sub(r'\s+', ' ', input_string.strip())
        
        # Find all complete dictionaries
        pattern = r'\{[^}]+\}'
        dict_strings = re.findall(pattern, input_string)
        
        result = []
        for dict_string in dict_strings:
            try:
                # Use ast.literal_eval to safely evaluate the dictionary string
                parsed_dict = ast.literal_eval(dict_string)
                result.append(parsed_dict)
            except (SyntaxError, ValueError):
                # If there's an error (likely due to an incomplete dictionary),
                # we'll parse it manually
                partial_dict = {}
                for item in re.findall(r"'(\w+)':\s*(\[[^\]]*\]|'[^']*')", dict_string):
                    key, value = item
                    try:
                        partial_dict[key] = ast.literal_eval(value)
                    except (SyntaxError, ValueError):
                        # If we can't evaluate, store as string
                        partial_dict[key] = value.strip("'")
                result.append(partial_dict)
        
        return result
    


    def _image_to_dict(self, image_source):
     

        description_dict = self.moondream.answer_question(
                    self.moondream.encode_image(image_source),
                    "Describe.",
                    tokenizer=self.tokenizer,
                    num_beams=2,
                    repetition_penalty=1.2,
                )
        description_dict=self._parse_incomplete_array(description_dict)
        
        return description_dict
        


    def label(self, image_source):
        if isinstance(image_source, str):
            if self.CHATGPT:
                clothes=describe_image_by_chatgpt(image_source)
                product_list=[clothe.to_dict() for clothe in clothes]
                return product_list
            image_source = url_to_pil_image(image_source)
        product_list = self._image_to_dict(image_source)
        return product_list
    
    
    def encode(self, image_sources):
        if isinstance(image_sources, str):
            image_sources = url_to_pil_image(image_sources)
        return self.moondream.encode_image(image_sources)

        
