
from transformers import AutoProcessor, AutoModel
from beam import env
import torch.nn.functional as F
import numpy as np
import torch
from blushy.utils.base import url_to_pil_image
import json
from blushy.utils.base import deserialize_embedding

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


    def encode_image(self,image_source):
        return self.get_embeddings(image_source)
        
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
    
    def classify(self, image, labels):
        if isinstance(labels, str):
            labels = [labels]
        text_descriptions = [f"This is a photo of a {label}" for label in labels]

        inputs = self.processor(text=text_descriptions, images=image, padding=True, return_tensors="pt")

        with torch.no_grad():
            results = self.model(**inputs)

        logits_per_image = results.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1).cpu().numpy()
        return probs

    def is_human(self,image_source):
        if isinstance(image_source,str):
            image_source=url_to_pil_image(image_source)

        classes=self.classify(image_source,["person body with face","clothe without face and body"])[0]
        print(classes)
        return classes[0]>classes[1]

    
    
import torch
import torch.nn as nn
from blushy.utils.base import deserialize_embedding

class RegionEmbeddingTripletNetwork(nn.Module):
    def __init__(self, input_dim, embedding_dim=128):
        super().__init__()
        self.projection = nn.Linear(input_dim, embedding_dim)

    def forward(self, x):
        return self.projection(x)

class ImageEmbeddingManager(SiglipManager):
    def __init__(self, input_dim=1152, embedding_dim=128, device=None):
        super().__init__()
        if env.is_remote():
            model_path = "/volumes/model-weights/model-weigths/region_embedding_triplet_network.pt"
        else:
            model_path = "/Users/tolgagunduz/Documents/projects/blushyv2/trainer/image_reranking/region_embedding_triplet_network.pt"
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model = RegionEmbeddingTripletNetwork(input_dim, embedding_dim).to(self.device)
        self.embedding_model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.embedding_model.eval()

    def get_embeddings(self, image):
        # Get the original embedding using parent method
        original_embedding = super().get_embeddings(image)
        # Convert to torch tensor and project
        return self.get_embeddings_from_embeddings(original_embedding)

    def get_embeddings_from_embeddings(self, original_embedding):
        if isinstance(original_embedding,str):
            original_embedding=deserialize_embedding(original_embedding)
        with torch.no_grad():
            tensor_embedding = torch.tensor(original_embedding).float().to(self.device)
            projected_embedding = self.embedding_model(tensor_embedding)
        # Return as numpy array
    
        image_embeds = projected_embedding

        # Normalize the embeddings
        image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
        image_embeds_np = image_embeds.cpu().numpy()  # Use .cpu() if running on GPU
        return image_embeds_np
        


if __name__ == "__main__":
    image_embedding_manager = ImageEmbeddingManager()
    embedding = image_embedding_manager.get_embeddings(url_to_pil_image("https://static.ticimax.cloud/35414/uploads/urunresimleri/buyuk/su-gecirmez-erkek-kapusonlu-sisme-mont-5-b2fb.jpg"))
    print(embedding)