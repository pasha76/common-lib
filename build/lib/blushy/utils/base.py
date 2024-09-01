import requests
from PIL import Image as PILImage
from io import BytesIO
import json

def url_to_pil_image(url):
    response = requests.get(url)
    img = PILImage.open(BytesIO(response.content))
    
    return img


def deserialize_embedding(embedding_str):
    return json.loads(embedding_str)


def serialize_embedding(embedding):
    return json.dumps(embedding.tolist())