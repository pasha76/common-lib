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


def classify_chatgpt_json(messages, return_obj, max_tokens=1800):
    # Setting up OpenAI API client
    api_key = os.environ["CHATGPT_API_KEY"]
    client = OpenAI(api_key=api_key)

    # Calling GPT to get the detailed description
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        response_format={ "type": "json_object" }
    )
    
    # Parse the response into the provided Pydantic model
    response_text = completion.choices[0].message.content
    return return_obj.model_validate_json(response_text)

def classify_chatgpt(image_url: str,prompt:str,return_obj:BaseModel):
    
    content=[{"type": "text", "text": prompt}]
    if image_url:
        content=[{"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                        ]

    # Call the function to analyze the image
    res = classify_chatgpt_json(messages=[
        {
            "role": "system",
            "content": "You are an AI assistant that classifies based on the prompt for an e-commerce platform."
        },
        {
            "role": "user",
            "content": content
        }],
        return_obj=return_obj
    )

    return res



