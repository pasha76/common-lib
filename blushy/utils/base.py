import requests
from PIL import Image as PILImage
from io import BytesIO
import json
import imagehash
import hashlib
import urllib3
import numpy as np

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def url_to_pil_image(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return PILImage.open(BytesIO(response.content))

def image_to_hash(image):
    return str(imagehash.phash(image))

def text_to_hash(unique_string):
    hash_object = hashlib.sha256(unique_string.encode())
    return hash_object.hexdigest()


def concat(text_embedding,image_embedding):
    normalized_text_embedding = text_embedding / np.linalg.norm(text_embedding)
    normalized_image_embedding = image_embedding / np.linalg.norm(image_embedding)
    combined_embedding = np.concatenate([normalized_text_embedding, normalized_image_embedding])
    return combined_embedding


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
