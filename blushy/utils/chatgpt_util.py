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

    def to_dict(self):
        return {
            "clothe_type": self.clothe_type,
            "detailed_description": self.detailed_description,
            "style": self.style,
            "color": self.color,
            "pattern": self.pattern,
            "fabric_type": self.fabric_type,
            "shape_and_fit": self.shape_and_fit,
            "occasion": self.occasion
        }


class Clothes(BaseModel):
    clothes: list[Clothe]

    def to_dict(self):
        return {"clothes": [clothe.to_dict() for clothe in self.clothes]}
   


def analyze_image_by_chatgpt_json(messages,max_tokens=1000):

    api_key=os.environ["CHATGPT_API_KEY"]
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        response_format=Clothes,
    )
    return completion.choices[0].message.parsed.clothes


def describe_image_by_chatgpt(image_url: str):
    prompt = f"""
    
    You are tasked with describing the clothing items in a photo for an e-commerce platform. The goal is to provide extreme detail about each visible clothing item including glasses,shoes and bags to make it easily searchable. Focus on the following aspects:

    - **Clothing Type**: Identify and describe only the visible clothing items that fit into the types provided below.
    - **Detailed Description**: Write a detailed description similar to what you would find in an e-commerce store. Include features such as the type of fit (slim, regular, loose), key design elements, and any other unique features. Minimum 50 words.
    - **Style**: Describe the overall style of the clothing item (e.g., casual, formal, sporty, streetwear, etc.).
    - **Color**: Identify the dominant color, and any secondary colors, if applicable.
    - **Pattern**: Mention any patterns such as stripes, checks, florals, graphics, etc.
    - **Fabric Type**: Describe the material of the item (e.g., cotton, denim, leather, polyester).
    - **Shape and Fit**: Describe the silhouette (e.g., fitted, oversized, A-line, straight-leg, etc.) and fit (e.g., slim, relaxed, tight, etc.).
    - **Occasion**: Suggest appropriate occasions to wear the clothing item (e.g., casual, business, evening, etc.).
    - **Bounding Box (BBox)**: Include the coordinates of the bounding box where the clothing item appears in the image, formatted as [x1, y1, x2, y2].

    example output:
    [
    {{
        "clothe_type": "Denim Shirt",
        "detailed_description": "This button-up denim shirt features an oversized fit that offers both comfort and a stylish silhouette. It has a unique light blue tie-dye wash that adds a modern twist to the classic denim look. The shirt is designed with a deep V-neck collar and long sleeves, making it versatile for layering or wearing alone. Perfect for casual outings or streetwear ensembles, it has a relaxed fit and is crafted from a durable cotton denim fabric.",
        "style": "Casual",
        "color": "Light Blue",
        "pattern": "Tie-dye",
        "fabric_type": "Cotton Denim",
        "shape_and_fit": "Oversized, Relaxed Fit",
        "occasion": "Casual, Streetwear"
    }},
    {{
        "clothe_type": "Denim Jeans",
        "detailed_description": "These high-waisted denim jeans feature a matching light blue tie-dye pattern that complements the shirt. The jeans are straight-leg, providing a classic silhouette that is both timeless and flattering. They include standard features such as belt loops, a zip fly, and pockets. Made from high-quality cotton denim, these jeans are ideal for casual daywear or an evening out when paired with a stylish top.",
        "style": "Casual",
        "color": "Light Blue",
        "pattern": "Tie-dye",
        "fabric_type": "Cotton Denim",
        "shape_and_fit": "Straight-leg, High-waisted",
        "occasion": "Casual, Daywear"
    }},
    {{
        "clothe_type": "Belt",
        "detailed_description": "A statement silver belt with an intricate design that complements the denim outfit. The belt adds a touch of sparkle and sophistication to the casual look, enhancing the waistline and tying the outfit together.",
        "style": "Statement, Casual",
        "color": "Silver",
        "pattern": "Textured, Metallic",
        "fabric_type": "Metal",
        "shape_and_fit": "Slim, Adjustable Fit",
        "occasion": "Casual, Streetwear, Evening Wear"
    }},
    {{
        "clothe_type": "Mini Handbag",
        "detailed_description": "A small, structured metallic handbag with a silver finish, featuring a short handle and minimalistic design. It adds a chic touch to the outfit while being practical for carrying essentials.",
        "style": "Elegant, Casual",
        "color": "Silver",
        "pattern": "Plain, Metallic",
        "fabric_type": "Leather",
        "shape_and_fit": "Small, Boxy",
        "occasion": "Casual, Evening Out"
    }},
    {{
        "clothe_type": "Black Leather Shoes",
        "detailed_description": "Black leather shoes with a rounded toe, designed in a simple, elegant style that complements the casual denim look. The shoes have a subtle platform, adding height and balance to the outfit without overpowering the overall look.",
        "style": "Casual, Streetwear",
        "color": "Black",
        "pattern": "Plain",
        "fabric_type": "Leather",
        "shape_and_fit": "Rounded Toe, Slight Platform",
        "occasion": "Casual, Daywear, Evening Out"
    }}
    ]
    
    Structure your output as a JSON object, with each clothing type being a key.
    
    Format your as JSON response like this:
    
    [
        {{
            "clothe_type": "<standard clothing type>",
            "detailed_description": "<detailed ecommerce-style description>",
            "style": "<style of the clothing item>",
            "color": "<dominant and secondary colors>",
            "pattern": "<pattern of the clothing item>",
            "fabric_type": "<type of fabric>",
            "shape_and_fit": "<shape and fit of the clothing item>",
            "occasion": "<appropriate occasions>"
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