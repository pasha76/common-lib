
from transformers import AutoProcessor, AutoModel
from beam import env
import torch.nn.functional as F
import numpy as np
import torch
from blushy.utils.base import url_to_pil_image
import json


class SiglipManager:

    def __init__(self) -> None:
        #model_name="google/siglip-base-patch16-224"
        model_name = "google/siglip-so400m-patch14-384"
        if env.is_remote():
            cache_path= "/volumes/model-weights/model-weigths/"
            self.model = AutoModel.from_pretrained(model_name,cache_dir=cache_path)
            self.processor = AutoProcessor.from_pretrained(model_name,cache_dir=cache_path)
        else:
            self.model = AutoModel.from_pretrained(model_name)
            self.processor = AutoProcessor.from_pretrained(model_name)


    def get_embeddings(self,image_source):
        if isinstance(image_source,str):
            image_source = url_to_pil_image(image_source)

        inputs = self.processor(images=image_source, return_tensors="pt")
        # Get model outputs
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)

        # Extract image embeddings
        image_embeds = outputs

        # Normalize the embeddings
        image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
        image_embeds_np = image_embeds.cpu().numpy()  # Use .cpu() if running on GPU
        return image_embeds_np
   

    def serialize_embedding(self,embedding):
        return json.dumps(embedding.tolist())
    
    def classify(self,image,labels):
        if isinstance(labels,str):
            labels =[labels]
        text_descriptions = [f"This is a photo of a {label}" for label in labels]

        inputs = self.processor(text=text_descriptions, images=[image], padding="max_length", return_tensors="pt")

        with torch.no_grad():
            self.model.config.torchscript = False
            results = self.model(**inputs)

        logits_per_image = results['logits_per_image']  # this is the image-text similarity score
       

        probs = logits_per_image.softmax(dim=1).detach().numpy().astype(float)
        return probs


    
    