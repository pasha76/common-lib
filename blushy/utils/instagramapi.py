import os
import requests
from PIL import Image
from io import BytesIO
class InstagramApi:
    
    def __init__(self, api_key="4Ypl2A3OAKmshxa6FBGripQK0Htjp1Z79R0jsnPKVK5x9U1c2F"):
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram28.p.rapidapi.com"
        }
        
    
    
    def find_instagram_media_urls(self,json_obj):
        """Recursively search for 'display_url', '__typename', and 'edge_liked_by'."""
        media_data = []
        
        if isinstance(json_obj, dict):
            # Check for 'display_url', '__typename', and 'edge_liked_by' criteria
            if json_obj.get('__typename') == "GraphImage"  and "display_url" in json_obj:
                data_dict = {"display_url": json_obj["display_url"],"instagram_post_id": json_obj["id"],"likes_count":0}
                
                # If edge_liked_by is present, extract its 'count' value and add it to the data_dict
                if "edge_media_preview_like" in json_obj and "count" in json_obj["edge_media_preview_like"]:
                    data_dict["likes_count"] = json_obj["edge_media_preview_like"]["count"]
                    
                media_data.append(data_dict)
            else:
                for v in json_obj.values():
                    if isinstance(v, (dict, list)):
                        media_data.extend(self.find_instagram_media_urls(v))
        elif isinstance(json_obj, list):
            for item in json_obj:
                if isinstance(item, (dict, list)):
                    media_data.extend(self.find_instagram_media_urls(item))

        return media_data


    def get_user_basic_info(self, user_name):
        url = "https://instagram28.p.rapidapi.com/user_info"
        params = {"user_name": user_name}
        response = requests.get(url, headers=self.headers, params=params)
        if len(response.json())==0:
            return []
        #print(response.json())
        data= response.json()["data"]
        infos=[]
        if data:
            user=data["user"]
         
            user_id=user["id"]
            user={"username":user_name,
                  "profile_photo_url":user["profile_pic_url"],
                  "follower_count":user["edge_followed_by"]["count"],
                  "following_count":user["edge_follow"]["count"],
                  "full_name":user["full_name"],
                  "is_verified":user["is_verified"],
                  "instagram_id":user_id
                  }
        return user
    

    def get_user_medias(self, user_id,batch_size=50):
        tmp_json=self.get_medias(user_id,batch_size)
        return self.find_instagram_media_urls(tmp_json)

    def get_medias(self, user_id, batch_size=50):
        
        url = "https://instagram28.p.rapidapi.com/medias"
        params = {"user_id": user_id, "batch_size": str(batch_size)}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_username_by_id(self, user_id):
    

        url = "https://instagram28.p.rapidapi.com/username"

        querystring = {"user_id":user_id}

        headers = {
            "X-RapidAPI-Key": "4Ypl2A3OAKmshxa6FBGripQK0Htjp1Z79R0jsnPKVK5x9U1c2F",
            "X-RapidAPI-Host": "instagram28.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        username = response.json()["user"]["username"]
        return username