from pydantic import BaseModel
from openai import OpenAI
import os

class Clothe(BaseModel):
    clothe_type: str
    detailed_description: str
    style: str
    color: str
    pattern: str
    fabric_type: str
    shape_and_fit: str
    occasion: str
    bbox: tuple[float, float, float, float]

class Clothes(BaseModel):
    clothes: list[Clothe]


def analyze_image_by_chatgpt_json(messages,max_tokens=1000):

    api_key=os.environ["CHATGPT_API_KEY"]
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=messages,
        max_tokens=max_tokens,
        response_format=Clothes,
    )
    return completion.choices[0].message.parsed


def describe_image_by_chatgpt(image_url: str):
    prompt = f"""
    
    You are tasked with describing the clothing items in a photo for an e-commerce platform. The goal is to provide extreme detail about each visible clothing item to make it easily searchable. Focus on the following aspects:

    - **Clothing Type**: Identify and describe only the visible clothing items that fit into the types provided below.
    - **Detailed Description**: Write a detailed description similar to what you would find in an e-commerce store. Include features such as the type of fit (slim, regular, loose), key design elements, and any other unique features. Minimum 50 words.
    - **Style**: Describe the overall style of the clothing item (e.g., casual, formal, sporty, streetwear, etc.).
    - **Color**: Identify the dominant color, and any secondary colors, if applicable.
    - **Pattern**: Mention any patterns such as stripes, checks, florals, graphics, etc.
    - **Fabric Type**: Describe the material of the item (e.g., cotton, denim, leather, polyester).
    - **Shape and Fit**: Describe the silhouette (e.g., fitted, oversized, A-line, straight-leg, etc.) and fit (e.g., slim, relaxed, tight, etc.).
    - **Occasion**: Suggest appropriate occasions to wear the clothing item (e.g., casual, business, evening, etc.).
    - **Bounding Box (BBox)**: Include the coordinates of the bounding box where the clothing item appears in the image, formatted as [x1, y1, x2, y2].
    
    Structure your output as a JSON object, with each clothing type being a key.
    
    Format your response like this:
    
    [
        {{
            "clothe_type": "<standard clothing type>",
            "detailed_description": "<detailed ecommerce-style description>",
            "style": "<style of the clothing item>",
            "color": "<dominant and secondary colors>",
            "pattern": "<pattern of the clothing item>",
            "fabric_type": "<type of fabric>",
            "shape_and_fit": "<shape and fit of the clothing item>",
            "occasion": "<appropriate occasions>",
            "bbox": [<x1>, <y1>, <x2>, <y2>]
        }},
        ...
    ]

    Ensure you only describe visible clothing and accessories in the image and keep the format structured and consistent.
    """

    res = analyze_image_by_chatgpt_json(messages=[
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
    return res