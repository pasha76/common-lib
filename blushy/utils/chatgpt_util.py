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




class Clothe(BaseModel):
    clothe_type: str
    detailed_description: str
    style: str
    color: List[str]  # Specify the type of items in the list
    pattern: str
    fabric_type: str
    shape_and_fit: str
    occasion_type: str
    pose_and_movement: str
    unique_features: List[str]  # Specify the type of items in the list
    bounding_box:List[int]

    def to_dict(self):
        return {
            "clothe_type": self.clothe_type,
            "detailed_description": self.detailed_description,
            "style": self.style,
            "color": self.color,
            "pattern": self.pattern,
            "fabric_type": self.fabric_type,
            "shape_and_fit": self.shape_and_fit,
            "occasion_type": self.occasion_type,
            "pose_and_movement": self.pose_and_movement,
            "unique_features": self.unique_features,
            "bounding_box":self.bounding_box
        }

class Clothes(BaseModel):
    clothes: List[Clothe]
    
    def to_dict(self):
        return [clothe.to_dict() for clothe in self.clothes]



def analyze_image_by_chatgpt_json(image, prompt, max_tokens=8192,credentials=None):
    if credentials:
        credentials = service_account.Credentials.from_service_account_file(credentials)
    else:
        credentials = service_account.Credentials.from_service_account_file("/Users/tolgagunduz/Documents/projects/blushyv2/app/creds/vertex/fashion-maidentech-3b1a88b308ed.json")
    # Setting up Gemini API client
    #genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    vertexai.init(
        project="fashion-maidentech", 
        location="us-central1",
        credentials=credentials
    )


    model = GenerativeModel("gemini-1.5-flash-002")

    generation_config = {
        "temperature": 0.,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": max_tokens,
        "response_mime_type": "application/json",
    }

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


def old_analyze_image_by_chatgpt_json(messages, max_tokens=1800):
    # Setting up OpenAI API client
    api_key = os.environ["CHATGPT_API_KEY"]
    client = OpenAI(api_key=api_key)

    # Calling GPT to get the detailed description
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        response_format=Clothes,
    )
    
    # Returning the parsed clothes descriptions
    return completion.choices[0].message.parsed.clothes

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
    2. **Detailed Description**: Write a comprehensive description that could be used for an e-commerce listing. Include key details such as the cut, shape, fit, any special features (e.g., ruffles, embroidery, zippers, etc.), and pose-related details (e.g., how the clothing drapes or fits in the image, such as a billowing skirt or snug jacket). This description should include a minimum of 75 words.
    3. **Style**: Classify the overall style of the item (e.g., casual, formal, sporty, elegant, vintage, streetwear, etc.). Describe any fashion trends or design influences.
    4. **Color**: Identify the dominant and any secondary colors. If the item has a distinct color contrast, gradient, or color-blocking, include those details.
    5. **Pattern**: Mention any visible patterns (e.g., stripes, florals, animal print, graphics, geometric designs, etc.), or specify if the item is solid.
    6. **Fabric Type**: Identify the fabric or material (e.g., cotton, leather, denim, silk, polyester). If the texture is visible (e.g., ribbed, smooth, quilted), describe it.
    7. **Shape and Fit**: Specify the item's silhouette (e.g., fitted, oversized, A-line, cropped) and the type of fit (e.g., slim, loose, tailored). If accessories like belts or ties adjust the fit, mention them.
    8. **Fit Type**: Provide specific fit types like "Slim", "Relaxed", or "Skinny".
    9. **Seasonality**: Describe the season this item is most appropriate for (e.g., Summer, Winter).
    10. **Weather Appropriateness**: Suggest the type of weather the item is suited for (e.g., Rainy, Cold Weather).
    11. **Color Family**: Categorize the colors into broader families (e.g., Neutrals, Brights).
    12. **Occasion**: Suggest appropriate occasions for wearing the item (e.g., casual, business, party, athletic).
    13. **Occasion Type**: Describe specific occasion types like "Beach Vacation", "Weddings", etc.
    14. **Fashion Trends**: Identify any specific fashion trends the item fits into (e.g., Y2K, Streetwear).
    15. **Pose and Movement**: If relevant, describe how the item is worn or displayed in the image (e.g., how a dress flows, how shoes fit, or the way glasses are perched on the nose).
    16. **Unique Features**: Highlight any standout details that make the item unique, such as embellishments, fastenings, stitching, or specific cuts (e.g., asymmetrical hems, double-breasted jackets, statement sleeves).
   

    Example output:

    [
    {{
        "clothe_type": "Sunglasses",
        "detailed_description": "These oversized sunglasses feature a bold frame with a glossy finish that instantly draws attention. The lenses are tinted, providing UV protection while adding an air of mystery. The wide arms of the sunglasses complement the face's shape and provide a stylishly sophisticated look. Perfect for sunny days, they add a trendy flair to any outfit.",
        "style": "Fashion-forward",
        "color": ["Black","white"],
        "pattern": "Solid",
        "fabric_type": "Plastic frame",
        "shape_and_fit": "Oversized frame",
        "fit_type": "Loose",
        "occasion_type": "Casual wear",
        "pose_and_movement": "Perched stylishly on the face, the sunglasses enhance the confident pose of the wearer.",
        "unique_features": "Oversized frame, tinted lenses",
        "bounding_box":[100,200,306,505]
    }},
    {{
        "clothe_type": "Tote Bag",
        "detailed_description": "A spacious tote bag with a minimalist geometric design in muted tones. The durable canvas with leather trims ensures practicality and style, while the interior features multiple pockets for organization.",
        "style": "Everyday Classic",
        "color": ["Off-white with tan accents","yellow"],
        "pattern": "Geometric",
        "fabric_type": "Canvas with leather trims",
        "shape_and_fit": "Spacious tote with shoulder straps",
        "occasion_type": "Everyday wear",
        "pose_and_movement": "Worn slung over one shoulder for practicality and style.",
        "unique_features": "Geometric design, multiple interior pockets",
        "bounding_box":[24,120,240,600]
    }},
    {{
        "clothe_type": "Sneakers",
        "detailed_description": "Metallic gold sneakers with a rounded toe and lace-up front. They feature a cushioned insole for comfort and a sleek design for casual and athletic wear.",
        "style": "Sporty Casual",
        "color": ["Gold"],
        "pattern": "Solid",
        "fabric_type": "Synthetic",
        "shape_and_fit": "Casual fit, cushioned insole",
        "occasion_type": "Everyday wear",
        "pose_and_movement": "Shown at an angle to highlight comfort and style.",
        "unique_features": "Metallic gold finish, lace-up front",
        "bounding_box":[56,85,124,432]
    }}
    ]


    Your response must follow this format, structured as a JSON object:
        [
        {{
            "clothe_type": "{clothe_types}",
            "detailed_description": "<detailed e-commerce style description as string>",
            "style": "<overall style as string>",
            "color": ["<dominant color>","<secondary color>"...],
            "pattern": "<any patterns or designs as string>",
            "fabric_type": "<material or fabric type as string>",
            "shape_and_fit": "<silhouette and fit as string>",
            "occasion_type": "<specific occasion type (e.g., Weddings, Beach Vacation) as string>",
            "pose_and_movement": "<details about how the item is worn or displayed in the image>",
            "unique_features": ["<special feature>"...],
            "bounding_box":[x1,y1,x2,y2]
        }},
        ...
        ]
        
        """

    # Call the function to analyze the image
    """res = analyze_image_by_chatgpt_json(messages=[
        {
            "role": "system",
            "content": "You are an AI that provides detailed, structured clothing descriptions based on images for an e-commerce platform."
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}]
        }
    ])
    """
    res = analyze_image_by_chatgpt_json(image_url,prompt,credentials=credentials)
    print(res)
    return res



if __name__=="__main__":
    describe_image_by_chatgpt("https://storage.googleapis.com/blushy-posts-maidentech/f2e1df5d71464bf2406ee93e25767fc5b6bd8495ac7dc3eb65b75c8fa4c896b7.jpg")
