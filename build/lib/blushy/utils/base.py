import requests
from PIL import Image as PILImage
from io import BytesIO

def url_to_pil_image(url):
    response = requests.get(url)
    img = PILImage.open(BytesIO(response.content))
    
    return img
