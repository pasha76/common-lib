from pydantic import BaseModel, Field
from openai import OpenAI
import os
from typing import List
import json
import google.generativeai as genai
from blushy.utils.base import url_to_pil_image
import vertexai

from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
import base64




class Clothe(BaseModel):
    clothe_type: str
    style: str
    color: List[str]  # Specify the type of items in the list
    pattern: str
    fabric_type: str
    shape_and_fit: str
    occasion_type: str | None = None
    unique_features: List[str]  # Specify the type of items in the list

    def to_dict(self):
        return {
            "clothe_type": self.clothe_type,
            "style": self.style,
            "color": self.color,
            "pattern": self.pattern,
            "fabric_type": self.fabric_type,
            "shape_and_fit": self.shape_and_fit,
            "occasion_type": self.occasion_type,
            "unique_features": self.unique_features,
        }

class Clothes(BaseModel):
    clothes: List[Clothe]
    
    def to_dict(self):
        return [clothe.to_dict() for clothe in self.clothes]



def analyze_image_by_chatgpt_json(image, prompt, max_tokens=500,credentials=None):
    

    vertexai.init(
        project="fashion-maidentech", 
        location="us-central1",
        credentials=credentials
    )


    model = GenerativeModel("gemini-1.5-flash-001")

    generation_config = {
        "temperature": 0.,
        "top_p": 0.55,
        "top_k": 2,
        "max_output_tokens": max_tokens,
        "response_mime_type": "application/json",
    }
    if image.startswith("http://") or image.startswith("https://"):
        image = Part.from_uri(
                mime_type="image/jpeg",
                uri=image,
            )

    else:
        image_bytes = base64.b64decode(image)
        image = Part.from_data(
            mime_type="image/jpeg",
            data=image_bytes,
        )
    response = model.generate_content(
        [image,prompt],
        generation_config=generation_config,
    )



    # Parse the JSON response and convert to Clothes object
    try:
        clothes_data = json.loads(response.text)
        return Clothes(clothes=[Clothe(**item) for item in clothes_data]).clothes
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}")



def describe_image_by_chatgpt(image_url: str,clothe_types:list=None,styles=None,colors=None,credentials=None):
    
    if clothe_types:
        clothe_types=("|").join(clothe_types)
    else:
        clothe_types="<standard clothing or accessory type>"
    
    if styles:
        styles=("|").join(styles)
    else:
        styles="<overall style>"

    if colors:
        colors=("|").join(colors)
    else:
        colors="<dominant and secondary colors>"
    # Define the improved prompt
    prompt = f"""
    
    You are tasked with describing the visible clothing items and accessories (including glasses, shoes, and bags) in a photo for an e-commerce platform. The goal is to provide extremely detailed descriptions of each visible item. Your descriptions should be specific, capturing any unique features, design elements, and distinct details that differentiate these items from similar products. Focus on the following aspects:
    
    1. **Clothing Type**: Identify and name only the visible clothing items and accessories. For example: "Maxi Dress", "Aviator Sunglasses", "Sneakers", "Crossbody Bag", etc.
    2. **Style**: Classify the overall style of the item (e.g., casual, formal, sporty, elegant, vintage, streetwear, etc.). Describe any fashion trends or design influences.
    3. **Color**: Identify the dominant and any secondary colors. If the item has a distinct color contrast, gradient, or color-blocking, include those details.
    4. **Pattern**: Mention any visible patterns (e.g., stripes, florals, animal print, graphics, geometric designs, etc.), or specify if the item is solid.
    5. **Fabric Type**: Identify the fabric or material (e.g., cotton, leather, denim, silk, polyester). If the texture is visible (e.g., ribbed, smooth, quilted), describe it.
    6. **Shape and Fit**: Specify the item's silhouette (e.g., fitted, oversized, A-line, cropped) and the type of fit (e.g., slim, loose, tailored). If accessories like belts or ties adjust the fit, mention them.
    7. **Fit Type**: Provide specific fit types like "Slim", "Relaxed", or "Skinny".
    8. **Fashion Trends**: Identify any specific fashion trends the item fits into (e.g., Y2K, Streetwear).
    9. **Unique Features**: Highlight any standout details that make the item unique, such as embellishments, fastenings, stitching, or specific cuts (e.g., asymmetrical hems, double-breasted jackets, statement sleeves).
   


    Your response must follow this format, structured as a JSON object:
        [
        {{
            "clothe_type": "{clothe_types}",
            "style": "<overall style as string>",
            "color": ["<dominant color>","<secondary color>"...],
            "pattern": "<any patterns or designs as string>",
            "fabric_type": "<material or fabric type as string>",
            "shape_and_fit": "<silhouette and fit as string>",
            "occasion_type": "<specific occasion type (e.g., Weddings, Beach Vacation) as string>",
            "unique_features": ["<special feature>"...],
        }},
        ...
        ]
        
        """

    res = analyze_image_by_chatgpt_json(image_url,prompt,credentials=credentials)
    print(res)
    return res



if __name__=="__main__":
    
    import time
    start = time.time()
  
    describe_image_by_chatgpt("https://i.pinimg.com/736x/5f/0d/1a/5f0d1a28be215d45e342fcc39ea92b07.jpg",credentials=None)

    print(time.time()-start)