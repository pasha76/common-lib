import os
import requests
from PIL import Image
from io import BytesIO

import requests
import json

class InstagramApi:
    """
    Instagram kullanıcı gönderilerini ve temel profil bilgilerini
    RapidAPI Instagram Scraper API'si aracılığıyla çeken sınıf.
    """
    def __init__(self, api_key="0c787cdf12msh6918cc0e08fb336p17d56cjsn8f7ba0e92b06"):
        """
        Sınıfı başlatır.
        :param api_key: RapidAPI anahtarınız.
        """
        self.posts_url = "https://instagram-scraper-stable-api.p.rapidapi.com/get_ig_user_posts.php"
        # Yeni profil bilgisi endpoint'i
        self.profile_hover_url = "https://instagram-scraper-stable-api.p.rapidapi.com/ig_get_fb_profile_hover.php"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "instagram-scraper-stable-api.p.rapidapi.com",
            # Bu Content-Type sadece POST istekleri için geçerlidir, GET için gerekli değildir.
            # Ancak headers sözlüğünde tutmak sorun yaratmaz.
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _make_api_request(self, method, url, params=None, data=None ):
        """
        API'ye istek gönderir ve JSON yanıtını döndürür.
        Yardımcı bir özel metottur. GET veya POST metodunu destekler.
        """
        try:
            if method.upper() == "POST":
                response = requests.post(url, data=data, headers=self.headers)
            elif method.upper() == "GET":
                response = requests.get(url, params=params, headers=self.headers)
            else:
                raise ValueError("Desteklenmeyen HTTP metodu. 'GET' veya 'POST' kullanın.")

            response.raise_for_status()  # HTTP hataları için istisna fırlatır (4xx veya 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API isteği sırasında bir hata oluştu: {e}")
            return None
        except json.JSONDecodeError:
            print("API yanıtı geçerli bir JSON değil.")
            return None
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")
            return None

    def get_user_images(self, username, amount=12):
        """
        Belirtilen Instagram kullanıcısının gönderilerinden görüntü URL'lerini alır.
        :param username: Instagram kullanıcı adı (örneğin, "yungfilly").
        :param amount: Alınacak gönderi sayısı (varsayılan 12).
        :return: Görüntü URL'lerinin bir listesi veya hata durumunda boş liste.
        """
        payload = {
            "username_or_url": f"https://www.instagram.com/{username}/",
            "amount": str(amount )
        }
        data = self._make_api_request("POST", self.posts_url, data=payload)

        image_urls = []
        if data and "posts" in data:
            for post in data["posts"]:
                node = post.get("node")
                if node:
                    # Carousel gönderileri için ek kontrol (media_type 8)
                    if node.get("media_type") == 8 and "carousel_media" in node:
                        for carousel_item in node["carousel_media"]:
                            if "image_versions2" in carousel_item and "candidates" in carousel_item["image_versions2"]:
                                # Genellikle ilk aday en yüksek çözünürlüklü olanıdır
                                if carousel_item["image_versions2"]["candidates"]:
                                    image_urls.append(carousel_item["image_versions2"]["candidates"][0]["url"])
                    # Tekli fotoğraf veya video gönderileri
                    elif "image_versions2" in node and "candidates" in node["image_versions2"]:
                        # Genellikle ilk aday en yüksek çözünürlüklü olanıdır
                        if node["image_versions2"]["candidates"]:
                            image_urls.append(node["image_versions2"]["candidates"][0]["url"])
        return image_urls

    def get_user_info(self, username):
        """
        Belirtilen Instagram kullanıcısının temel profil bilgilerini alır
        (takipçi sayısı, takip edilen sayısı, tam ad, profil fotoğrafı).
        :param username: Instagram kullanıcı adı.
        :return: Kullanıcı bilgilerini içeren bir sözlük veya hata durumunda None.
        """
        querystring = {
            "username_or_url": username
        }
        # Yeni endpoint'i ve GET metodunu kullanıyoruz
        data = self._make_api_request("GET", self.profile_hover_url, params=querystring)

        if data and "user_data" in data:
            user_data = data["user_data"]
            user_info = {
                "follower_count": user_data.get("follower_count"),
                "following_count": user_data.get("following_count"),
                "full_name": user_data.get("full_name"),
                "username": user_data.get("username"),
                "profile_pic_url": user_data.get("profile_pic_url"),
                "is_verified": user_data.get("is_verified")
            }
            return user_info
        return None

class InstagramApi_OLD:
    
    def __init__(self, api_key="0c787cdf12msh6918cc0e08fb336p17d56cjsn8f7ba0e92b06"):
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