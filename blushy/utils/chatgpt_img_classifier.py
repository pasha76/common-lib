from pydantic import BaseModel, Field
from openai import OpenAI
import os
from typing import List

class Info(BaseModel):
    full_body_human: bool
    partial_body_human: bool
    no_human: bool
    clothe_wearables:bool
    more_than_one_person: bool
    aesthetic_score: int

class Infos(BaseModel):
    info: Info = Field(..., alias="infos")

def analyze_image_by_chatgpt_json(messages, max_tokens=1800):
    # Setting up OpenAI API client
    api_key = os.environ["CHATGPT_API_KEY"]
    client = OpenAI(api_key=api_key)

    # Calling GPT to get the detailed description
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        response_format=Infos,
    )
    
    # Returning the parsed clothes descriptions
    return completion.choices[0].message.parsed.info

def classify_image_by_chatgpt(image_url: str):
    
    # Define the improved prompt
    prompt = f"""
    
    You are an AI image classifier. I will provide you with an image, and you need to classify it into the following categories. For each category, return a boolean value indicating whether the image fits that category. The categories are:

	1.	Full body human: Does the image contain a whole human body entirely visible from head to toe?
	2.	Partial body human: Does the image contain only part of a human figure (e.g., head, torso, arms, or legs), but not the whole body?
	3.	No human: Does the image contain no visible humans?
	4.	Clothe (wearables): Does the image primarily focus on clothing items or accessories such as shirts, pants, dresses, bags, shoes, etc.?
	5.	More than one person: Does the image contain more than one person?

    In addition, return an aesthetic score for the image, rated from 1 to 10, where 10 indicates the best quality image (well-lit, well-composed, details are visible) and 1 indicates the worst quality (dark, blurry, or not perfectly visible).

    Please return the results in the following JSON format:
            {{
            "full_body_human": true/false,
            "partial_body_human": true/false,
            "no_human": true/false,
            "clothe_wearables": true/false,
            "more_than_one_person": true/false,
            "aesthetic_score": score_value
            }}
        """

    # Call the function to analyze the image
    res = analyze_image_by_chatgpt_json(messages=[
        {
            "role": "system",
            "content": "You are an AI image classifier that classifies based on images for an e-commerce platform."
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}]
        }
    ])

    return res



