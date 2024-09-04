from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
from beam import env

class TextSimilarity:
    def __init__(self, model_name='all-MiniLM-L6-v2', device='cpu'):
        """
        Initializes the TextSimilarity class with a specified SentenceTransformer model and device.
        
        :param model_name: The name of the pre-trained model to use for generating embeddings.
                           Default is 'all-MiniLM-L6-v2'.
        :param device: The device to run the model on ('cpu' or 'cuda'). Default is 'cpu'.
        """
        self.device = device
        if env.is_remote():
            cache_path= "/volumes/model-weights/model-weigths/"
            self.model = SentenceTransformer(model_name, clean_up_tokenization_spaces=True, device=self.device, cache_folder=cache_path)
        else:
            self.model = SentenceTransformer(model_name, clean_up_tokenization_spaces=True, device=self.device)

    def encode_text(self, text):
        """
        Encodes a given text into an embedding vector using the SentenceTransformer model.
        
        :param text: The input text to encode.
        :return: A numpy array representing the embedding of the input text.
        """
        # Encode the text and convert the tensor to a numpy array
        embedding = self.model.encode(text, convert_to_tensor=True, device=self.device)
        embedding = embedding.cpu().numpy()  # Convert tensor to numpy array
        return embedding

    def find_similar(self, query_text, corpus, top_k=5):
        """
        Finds the most similar texts in a corpus to a given query text based on cosine similarity.
        
        :param query_text: The text for which similar texts are to be found.
        :param corpus: A list of texts against which the query text will be compared.
        :param top_k: The number of top similar texts to return. Default is 5.
        :return: A list of tuples containing the similar texts and their similarity scores.
        """
        # Encode the query text and corpus as numpy arrays
        query_embedding = self.encode_text(query_text)
        print(query_embedding.shape)
        corpus_embeddings = self.model.encode(corpus, convert_to_tensor=True, device=self.device).cpu().numpy()

        # Compute cosine similarities between the query embedding and all corpus embeddings
        cosine_scores = util.pytorch_cos_sim(torch.tensor(query_embedding), torch.tensor(corpus_embeddings))[0]

        # Get the top-k most similar texts
        top_results = np.argpartition(-cosine_scores, range(top_k))[:top_k]

        # Return the top-k similar texts and their cosine scores
        similar_texts = [(corpus[idx], float(cosine_scores[idx])) for idx in top_results]
        similar_texts = sorted(similar_texts, key=lambda x: x[1], reverse=True)

        return similar_texts

# Example usage
if __name__ == "__main__":
    # Initialize the TextSimilarity class
    text_similarity = TextSimilarity(
        model_name='all-Mpnet-base-v2',
        device='cuda' if torch.cuda.is_available() else 'cpu')

    # Define a query text
    query = "How to learn Python programming?"

    # Define a corpus of texts
    corpus = [
        "Python programming is fun.",
        "Learn to code in Python.",
        "How to cook Italian pasta?",
        "Python is a versatile language.",
        "Machine learning with Python.",
        "Just check web sites to learn Python.",
        "How can I learn Python?",
    ]

    # Find similar texts
    similar_texts = text_similarity.find_similar(query, corpus, top_k=3)

    # Print the results
    print("Similar texts to the query:")
    for text, score in similar_texts:
        print(f"Text: {text} (Score: {score:.4f})")