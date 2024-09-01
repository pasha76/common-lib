import requests
from google.cloud import storage
import hashlib
from PIL import Image as PILImage
import io
import os
import certifi
import time
import numpy as np


class GCSUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        
    def convert_to_sha256(self,string):
        # Create a sha256 hash object
        sha_signature = hashlib.sha256(string.encode()).hexdigest()
        return sha_signature

    def upload_image(self, image):
        """Fetches an image from a URL and uploads it to the bucket."""
        if type(image) is str:
            response = requests.get(image,verify=False)
            if response.status_code == 200:
                destination_blob_name=self.convert_to_sha256(image)
                blob = self.bucket.blob(destination_blob_name+".jpg")
                
                # Upload the image content
                blob.upload_from_string(response.content, content_type=response.headers['Content-Type'])
                
                # Make the blob publicly viewable
                #blob.make_public()
                
                # Return the public URL
                return blob.public_url
            
        if isinstance(image, PILImage.Image):
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Convert the PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Use SHA-256 hash of the image bytes as the blob name
            destination_blob_name = self.convert_to_sha256(str(img_byte_arr)) + ".jpg"
            blob = self.bucket.blob(destination_blob_name)

            # Upload the image content
            blob.upload_from_string(img_byte_arr, content_type='image/jpeg')
            
            # Make the blob publicly viewable
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
            
        if isinstance(image, np.ndarray):
            image = PILImage.fromarray(image)
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Convert the PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Use SHA-256 hash of the image bytes as the blob name
            destination_blob_name = self.convert_to_sha256(str(img_byte_arr)) + ".jpg"
            blob = self.bucket.blob(destination_blob_name)

            # Upload the image content
            blob.upload_from_string(img_byte_arr, content_type='image/jpeg')
            
            # Make the blob publicly viewable
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
        
        else:
            print(f"Failed to fetch image from URL:")
            return None

    def upload_csv(self, file_path, destination_blob_name=None):
        """Uploads a CSV file to the bucket and returns the public URL."""
        if destination_blob_name is None:
            destination_blob_name = os.path.basename(file_path)
            destination_blob_name=self.convert_to_sha256(f"{destination_blob_name}{time.time()}")+".csv"
        
        blob = self.bucket.blob(destination_blob_name)
        
        with open(file_path, 'rb') as file_obj:
            blob.upload_from_file(file_obj, content_type='text/csv')
        
        blob.make_public()
        uri=blob.public_url.replace("https://storage.googleapis.com/","gs://")
        return uri
    
    def delete_file(self, uri):
        """Deletes a file from the bucket using its URI."""
        try:
            # Extract the blob name from the URI
            blob_name = uri.replace("gs://", "").replace(f"{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_name)
            
            # Delete the blob
            blob.delete()
            return f"File {blob_name} deleted successfully."
        except Exception as e:
            return f"Failed to delete file: {str(e)}"