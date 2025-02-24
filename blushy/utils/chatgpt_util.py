from pydantic import BaseModel, Field
from openai import OpenAI
import os
from typing import List
import json
import google.generativeai as genai
from blushy.utils.base import url_to_pil_image
import vertexai
import base64
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
    seasonality:str
    weather_appropriateness:str
    fashion_trends:str
    occasion:str

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
            "seasonality":self.seasonality,
            "weather_appropriateness":self.weather_appropriateness,
            "fashion_trends":self.fashion_trends,
            "occasion":self.occasion
        }

    def to_sentence(self):
        try:
            # Extract main attributes with fallbacks
            clothe_type = self.clothe_type
            color = ', '.join(self.color) if self.color else 'unspecified color'
            style = self.style
            pattern = self.pattern
            fabric_type = self.fabric_type
            shape_and_fit = self.shape_and_fit
            occasion_type = self.occasion_type
            pose_and_movement = self.pose_and_movement
            unique_features = ', '.join(self.unique_features) if self.unique_features else 'no unique features'
            seasonality = self.seasonality
            weather = self.weather_appropriateness
            trends = self.fashion_trends
            occasion = self.occasion
            detailed_description = self.detailed_description

            # Create a description that emphasizes color and clothe_type through repetition
            # and strategic placement at the beginning and end of sentences
            description = (
                f"This is a {color} {clothe_type}. "
                f"The {clothe_type} features a {color} tone with {pattern} pattern. "
                f"This {style} {clothe_type} is made from {fabric_type} with a {shape_and_fit} fit. "
                f"Perfect for {occasion_type}, this {color} {clothe_type} {pose_and_movement}. "
                f"Notable features include {unique_features}. "
            )

            # Add optional attributes if they exist
            if seasonality:
                description += f"Ideal for {seasonality}. "
            if weather:
                description += f"Suitable for {weather} weather. "
            if trends:
                description += f"Follows {trends} trends. "
            if occasion:
                description += f"Perfect for {occasion}. "
            if detailed_description:
                description += f"{detailed_description} "

            return description.lower()  # Convert to lowercase for consistency

        except Exception:
            # Extract main attributes with fallbacks
            clothe_type = self.clothe_type
            color = ', '.join(self.color) if self.color else 'unspecified color'
            style = self.style
            pattern = self.pattern
            fabric_type = self.fabric_type
            shape_and_fit = self.shape_and_fit
            occasion_type = self.occasion_type
            pose_and_movement = self.pose_and_movement
            unique_features = ', '.join(self.unique_features) if self.unique_features else 'no unique features'
            detailed_description = self.detailed_description

            # Create a description that emphasizes color and clothe_type through repetition
            # and strategic placement at the beginning and end of sentences
            description = (
                f"This is a {color} {clothe_type}. "
                f"The {clothe_type} features a {color} tone with {pattern} pattern. "
                f"This {style} {clothe_type} is made from {fabric_type} with a {shape_and_fit} fit. "
                f"Perfect for {occasion_type}, this {color} {clothe_type} {pose_and_movement}. "
                f"Notable features include {unique_features}. "
            )
            return description.lower()
    

class Clothes(BaseModel):
    clothes: List[Clothe]
    
    def to_dict(self):
        return [clothe.to_dict() for clothe in self.clothes]



def analyze_image_by_chatgpt_json(image, prompt, max_tokens=8192,credentials=None):
    

    vertexai.init(
        project="fashion-maidentech", 
        location="us-central1",
        credentials=credentials
    )


    model = GenerativeModel("gemini-2.0-flash-001")

    generation_config = {
        "temperature": 0.,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": max_tokens,
        "response_mime_type": "application/json",
    }
    if image.startswith("http"):
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
    
    You are tasked with describing the visible clothing items and accessories (including glasses, shoes, and bags) in a photo for an e-commerce platform. The goal is to provide extremely detailed descriptions of each visible item in a manner that conveys tactile, visual, and spatial details as if explaining to a person who cannot see. Each description must be highly detailed, outlining all visible features and characteristics to allow a blind person to mentally visualize the item. Do not use personal adverbs such as “I,” “you,” or “we.” Instead, use objective, descriptive language focused solely on the item’s attributes.

    The description for each item must include the following aspects:
        1.	Clothing Type: Identify and name only the visible clothing items and accessories (e.g., “Maxi Dress”, “Aviator Sunglasses”, “Sneakers”, “Crossbody Bag”).
        2.	Detailed Description: Provide a comprehensive, e-commerce style description that includes the cut, shape, fit, and any special features (e.g., ruffles, embroidery, zippers). Describe how the clothing drapes, its contours, and any tactile details such as texture and stitching. The description should contain a minimum of 75 words.
        3.	Style: Classify the overall style (e.g., casual, formal, sporty, elegant, vintage, streetwear) and mention any relevant fashion trends or design influences.
        4.	Color: Identify the dominant and any secondary colors, describing any color contrasts, gradients, or color-blocking effects.
        5.	Pattern: Mention any visible patterns (e.g., stripes, florals, animal print, graphics, geometric designs) or indicate if the item is a solid color.
        6.	Fabric Type: Specify the material (e.g., cotton, leather, denim, silk, polyester) and describe the texture (e.g., ribbed, smooth, quilted) to convey a tactile sense.
        7.	Shape and Fit: Define the silhouette (e.g., fitted, oversized, A-line, cropped) and describe the fit (e.g., slim, loose, tailored). Include details such as the effect of belts or ties on the overall fit.
        8.	Fit Type: Clearly indicate specific fit types like “Slim,” “Relaxed,” or “Skinny.”
        9.	Seasonality: Describe the season the item is best suited for (e.g., Summer, Winter).
        10.	Weather Appropriateness: Suggest the type of weather (e.g., Rainy, Cold Weather) for which the item is ideal.
        11.	Color Family: Categorize the colors into broader groups (e.g., Neutrals, Brights).
        12.	Occasion: Suggest appropriate occasions for wearing the item (e.g., casual, business, party, athletic).
        13.	Occasion Type: Specify particular occasions such as “Beach Vacation,” “Weddings,” etc.
        14.	Fashion Trends: Identify any specific fashion trends that the item aligns with (e.g., Y2K, Streetwear).
        15.	Pose and Movement: Explain how the item is positioned, how it drapes or flows, and any visible movement in the image.
        16.	Unique Features: Highlight standout details (e.g., embellishments, fastenings, distinctive stitching, asymmetrical hems, double-breasted designs).

        The final output must be structured as a JSON array of objects, each representing one item. The JSON structure should be as follows:
            [
            {{
                "clothe_type": "{clothe_types}",
                "detailed_description": "<detailed e-commerce style visually and tactically accurate description including shape, texture, and other physical details as a string>",
                "style": "<overall style as string>",
                "color": ["<dominant color>", "<secondary color>", "..."],
                "pattern": "<any patterns or designs as string>",
                "fabric_type": "<material or fabric type as string>",
                "shape_and_fit": "<silhouette and fit as string>",
                "occasion_type": "<specific occasion type (e.g., Weddings, Beach Vacation, party, dinner, casual, business meeting, sports event, etc.) as string>",
                "pose_and_movement": "<detailed description of how the item is worn or displayed, emphasizing its drape, flow, and tactile characteristics>",
                "unique_features": ["<special feature>", "..."],
                "seasonality": "<seasonality as string>",
                "weather_appropriateness": "<weather appropriateness as string>",
                "fashion_trends": "<fashion trend>,<fashion trend>,<fashion trend> as string>",
                "occasion": "<occasion as string>"
            }},
            ...
            ]

            All descriptions should be free of personal adverbs and written in a neutral, descriptive tone to ensure the details are vivid and comprehensible to someone who cannot see the item.
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
    
    
    creds=service_account.Credentials.from_service_account_info(None)
  
    describe_image_by_chatgpt("https://i.pinimg.com/736x/5f/0d/1a/5f0d1a28be215d45e342fcc39ea92b07.jpg",credentials=creds)
