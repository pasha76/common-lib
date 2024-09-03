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



def dict_to_hashable(**d):
    """
    Convert a dictionary to a hashable tuple suitable for use as a cache key.

    :param d: Dictionary to convert.
    :return: Hashable tuple representation of the dictionary.
    """
    # Convert each key-value pair into a tuple, converting nested dictionaries recursively
    return tuple((k, dict_to_hashable(v) if isinstance(v, dict) else v) for k, v in sorted(d.items()))


def to_dict(arr,attr=None):
    if arr is None:
        return []
    if not isinstance(arr, list):
        return arr.to_dict()
    if attr:
        return [x.__getattribute__(attr).to_dict() for x in arr]
    return [x.to_dict() for x in arr]
