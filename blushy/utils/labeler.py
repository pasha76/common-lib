from beam import env
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from blushy.utils.base import url_to_pil_image
import xml.etree.ElementTree as ET
import time

# Set device and data type for CPU
DEVICE = "cpu"
DTYPE = torch.float32
MD_REVISION = "2024-07-23"
PATH= "/users/tolgagunduz/downloads/checkpoints/moondream-ft"

if env.is_remote():
    PATH= "/model-weights/model-weigths/moondream-ft/"

    


class Labeler:
    def __init__(self):
        print("Loading Moondream model...",PATH)
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

    def _parse_xml_to_dict(self,xml_string):
        xml_string = xml_string.split("</item>")[:-1]
        xml_string = "<items>"+"</item>\n ".join(xml_string)+"</item></items>"
        parsed_items = []
        
        try:
            # Parse the XML string
            root = ET.fromstring(xml_string)

            # Iterate through each 'item' element
            for item in root.findall('item'):
                try:
                    # Extract data from XML elements, with checks for NoneType
                    description = item.find('description').text if item.find('description') is not None else ''
                    color = item.find('color').text if item.find('color') is not None else ''
                    type_ = item.find('type').text if item.find('type') is not None else ''
                    style = item.find('style').text if item.find('style') is not None else ''
                    
                    # Append the parsed data as a dictionary to the list
                    parsed_items.append({
                        'description': description,
                        'color': color,
                        'type': type_,
                        'style': style
                    })
                except AttributeError as e:
                    print(f"Error parsing item element: {e}")
                    return None
                except Exception as e:
                    print(f"Unexpected error while parsing item: {e}")
                    return None

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while parsing XML: {e}")
            return None

        return parsed_items[0]

    def _image_to_xml(self, image_source):
        description_xml = self.moondream.answer_question(
                    self.moondream.encode_image(image_source),
                    "Describe.",
                    tokenizer=self.tokenizer,
                    num_beams=1,
                    repetition_penalty=1.2,
                    length_penalty=1000.
                )
        return description_xml

    def label(self, image_source):
        if isinstance(image_source, str):
            image_source = url_to_pil_image(image_source)
        xml_description=self._image_to_xml(image_source)
        return self._parse_xml_to_dict(xml_description)


        
