from sklearn.neighbors import NearestNeighbors
import numpy as np
from blushy.utils.base import url_to_pil_image,deserialize_embedding
from blushy.utils.siglip_manager import SiglipManager
from torch import embedding

class ItemImage:
    def __init__(self, embedding):
        self.embedding = np.array(embedding)

class ImageSorter:
    def __init__(self, item_images=[],siglip_manager=None):
        """
        Initializes the ImageSorter with a list of ItemImage objects.
        
        :param item_images: List of ItemImage objects
        """
   
        self.item_images = item_images
        self.nearest_neighbors = NearestNeighbors(n_neighbors=len(item_images), algorithm='auto')
        if len(item_images)>0:
            self.embeddings = np.array([deserialize_embedding(item.embedding)[0] for item in item_images if item.embedding is not None])
  
            self.embeddings = self.embeddings.reshape(self.embeddings.shape[0],-1)
            self.nearest_neighbors.fit(self.embeddings)
        self.siglip_manager = siglip_manager


    def sort_by_proximity(self, reference_embedding):
        """
        Sorts the ItemImage objects by their proximity to the reference embedding.
        
        :param reference_embedding: The embedding vector to compare against
        :return: A list of ItemImage objects sorted by proximity to the reference embedding
        """
        reference_embedding = np.array(reference_embedding).reshape(1, -1)
        distances, indices = self.nearest_neighbors.kneighbors(reference_embedding)
        #sorted_item_images = [(distance,self.item_images[idx]) for distance,idx in zip(distances.flatten(),indices.flatten())]


        # Convert distances to similarity percentages
        max_distance = np.max(distances)
        similarities = 100 * (1 - distances / max_distance)

        sorted_item_images = [(similarity, self.item_images[idx]) 
                            for similarity, idx in zip(similarities.flatten(), indices.flatten())]

        # Sort by similarity in descending order
        sorted_item_images.sort(key=lambda x: x[0], reverse=True)

        return sorted_item_images
    

    def image_already_exists(self,image_source,threshold=0.1):
        embedding = self.siglip_manager.get_embeddings(image_source)
        embedding = embedding.tolist()
        if len(self.item_images)==0:
            self.item_images.append(embedding)
            return False
        self.embeddings = np.array([item.embedding for item in  self.item_images])
        self.nearest_neighbors.fit(self.embeddings)
        reference_embedding = np.array(embedding).reshape(1, -1)
        distances, indices = self.nearest_neighbors.kneighbors(reference_embedding)
        if distances[0][0]<threshold:
            return True
        else:
            self.item_images.append(embedding)
            return False
        

        
        

# Example usage
if __name__ == "__main__":
    # Create some example ItemImage objects with embeddings
    images = [
        ItemImage([1.0, 2.0, 3.0]),
        ItemImage([4.0, 5.0, 6.0]),
        ItemImage([7.0, 8.0, 9.0]),
        ItemImage([2.0, 3.0, 1.0]),
    ]

    # Initialize the ImageSorter with the list of images
    sorter = ImageSorter(images)

    # Define a reference embedding to sort the images by proximity
    reference_embedding = [2.0, 3.0, 2.0]

    # Sort images by proximity to the reference embedding
    sorted_images = sorter.sort_by_proximity(reference_embedding)

    # Print sorted embeddings for verification
    print("Sorted ItemImage embeddings:")
    for image in sorted_images:
        print(image.embedding)