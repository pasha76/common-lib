from sklearn.neighbors import NearestNeighbors
import numpy as np

class ItemImage:
    def __init__(self, embedding):
        self.embedding = np.array(embedding)

class ImageSorter:
    def __init__(self, item_images):
        """
        Initializes the ImageSorter with a list of ItemImage objects.
        
        :param item_images: List of ItemImage objects
        """
        self.item_images = item_images
        self.embeddings = np.array([item.embedding for item in item_images])
        self.nearest_neighbors = NearestNeighbors(n_neighbors=len(item_images), algorithm='auto')
        self.nearest_neighbors.fit(self.embeddings)

    def sort_by_proximity(self, reference_embedding):
        """
        Sorts the ItemImage objects by their proximity to the reference embedding.
        
        :param reference_embedding: The embedding vector to compare against
        :return: A list of ItemImage objects sorted by proximity to the reference embedding
        """
        reference_embedding = np.array(reference_embedding).reshape(1, -1)
        distances, indices = self.nearest_neighbors.kneighbors(reference_embedding)
        sorted_item_images = [self.item_images[idx] for idx in indices.flatten()]

        return sorted_item_images

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