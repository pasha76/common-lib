from qdrant_client.models import PointStruct, QueryRequest,NamedVector
from qdrant_client.models import Distance, VectorParams, MatchValue, Filter, FieldCondition, MatchAny
from qdrant_client import QdrantClient, models
from qdrant_client.models import SearchRequest, SearchParams, Filter, FieldCondition, MatchValue
import os
from typing import List, Dict, Union, Optional
import numpy as np
from blushy.utils.base import deserialize_embedding


class VectorManager:
    def __init__(self, collection_name="vendors", vector_size=768, distance=Distance.COSINE,config=None):
        url = os.getenv('QDRANT_URL')
        api_key = os.getenv('QDRANT_API_KEY')
  
        self.client = QdrantClient(url=url, api_key=api_key, timeout=10)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        self.config=config

    def create_index(self, collection_name, field_name, field_schema):
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=field_schema)

    def recreate_collection(self):
        if self.config is None:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=self.distance),
            )
        else:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.config,
            )

    def update_metadata(self, idx, metadata):
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=metadata,
            points=idx,
        )

    def upsert_vectors(self, idx, vectors, metadata_list=None):
        if metadata_list is None:
            metadata_list = [{} for _ in range(len(vectors))]
        if len(vectors) != len(metadata_list):
            raise ValueError("Vectors and metadata list must have the same length.")

        points = [
            PointStruct(
                id=idx,
                vector=vector,
                payload=metadata
            )
            for idx, vector, metadata in zip(idx, vectors, metadata_list)
        ]

        # Note: Consider handling large batches in smaller chunks to avoid hitting server limits
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def recommend(self, positive_label_ids, negative_label_ids,  master_gender_id=1, country_id=1, limit=10, page=0):
        # Retrieve visited and clicked post IDs from metadata
     

        result= self.client.recommend(
            self.collection_name,
            positive=positive_label_ids,
            negative=negative_label_ids,
            with_payload=True,
            with_vectors=False,
            strategy=models.RecommendStrategy.BEST_SCORE,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="master_gender_id",
                        match=models.MatchValue(value=master_gender_id),
                    ),
                    models.FieldCondition(
                        key="country_id",
                        match=models.MatchValue(value=country_id),
                    ),
                    
                ],
            ),
            limit=limit,
            offset=page * limit
        )
        results=[]
        for item in result:
            results.append(item.payload["post_id"])
        return results,(limit+1)*page
    

    def search_by_batch(self, query_vectors):
        search_queries = [
            QueryRequest(query=qv)
            for qv in query_vectors
        ]
        assert len(search_queries) == len(query_vectors)

        return self.client.query_batch_points(collection_name=self.collection_name, requests=search_queries)

    def search_vectors(self, query_vector, filter=None, page=0, limit=20):
        filters = []
        if filter:
            for k, v in filter.items():
                filters.append(FieldCondition(
                    key=k,
                    match=MatchValue(
                        value=v,
                    ),
                ))

        filter = Filter(must=filters)
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter,
            limit=limit,
            offset=page * limit,
            score_threshold=None,
        )
        return result

    def search_from_vendor(self, query_vector, filter=None, page=0, limit=20):
        if filter:
            filter = Filter(
                must=[
                    FieldCondition(
                        key="master_gender_id",
                        match=MatchValue(
                            value=filter["master_gender_id"],
                        ),
                    ),
                    FieldCondition(
                        key="master_clothe_type_id",
                        match=MatchValue(
                            value=filter["master_clothe_type_id"],
                        ),
                    )
                ]
            )
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter,
            limit=limit,
            offset=page * limit,
            score_threshold=None,
        )
        return result

    def get_by_id(self, id):
        return self.client.retrieve(
            collection_name=self.collection_name,
            ids=[id],
        )

    def count_clothe_type(self, master_clothe_type_id):
        return self.client.count(
            collection_name=self.collection_name,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(key="master_clothe_type_id", match=models.MatchValue(value=master_clothe_type_id)),
                ]
            ),
            exact=True,
        )

    def delete_by_id(self, ids):
        if isinstance(ids, list):
            return self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids,
                ),
            )
        return self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=[ids],
            ),
        )

    def delete_by_filters(self, delete_filter):
        return self.client.delete(collection_name=self.collection_name, points_selector=delete_filter)

    def batch_search_vectors(self, query_vectors, filter=None, limit=20, page=0):
        """
        Perform batch search for multiple query vectors with optional filtering
        """
        filters = []
        if filter:
            for k, v in filter.items():
                filters.append(models.FieldCondition(
                    key=k,
                    match=models.MatchValue(
                        value=v,
                    ),
                ))

        filter_obj = models.Filter(must=filters) if filters else None

        # Create batch search queries
        search_queries = [
            models.SearchRequest(
                vector=qv,
                filter=filter_obj,
                limit=limit,
                offset=page * limit,
                with_payload=True
            )
            for qv in query_vectors
        ]

        # Execute batch search
        results = self.client.search_batch(
            collection_name=self.collection_name,
            requests=search_queries,
        )

        return results

    def batch_search_vector_with_filters(self, query_vectors, filter=None, limit=20, page=0):
        """
        Perform batch search for multiple query vectors with optional filtering.
        The search will return vectors that match ANY of the provided filters (OR condition).
        
        Args:
            query_vectors: List of query vectors to search for
            filter: List of tuples containing (key, value) pairs for filtering
            limit: Maximum number of results per query
            page: Page number for pagination
        """
        should_filters = []
        must_filters = []
        if filter:
            # Expecting filter to be a list of (key, value) tuples
            for k, v, c in filter:
                if c == "should":
                    should_filters.append(models.FieldCondition(
                        key=k,
                        match=models.MatchValue(
                            value=v,
                        ),
                    ))
                else:
                    must_filters.append(models.FieldCondition(
                        key=k,
                        match=models.MatchValue(
                            value=v,
                        ),
                    ))

        # Using should instead of must to implement OR logic between filters
        filter_obj = models.Filter(should=should_filters, must=must_filters)

        # Create batch search queries
        search_queries = [
            models.SearchRequest(
                vector=qv,
                filter=filter_obj,
                limit=limit,
                offset=page * limit,
                with_payload=True
            )
            for qv in query_vectors
        ]

        return self.client.search_batch(
            collection_name=self.collection_name,
            requests=search_queries,
        )


 
 

    def hybrid_search(self,
        query_text_vector, 
        query_image_vector, 
        text_weight=0.7,    # For future use; not applied natively yet
        image_weight=0.3,   # For future use; not applied natively yet
        master_gender_id=None, 
        country_id=None, 
        master_clothe_type_id=None, 
        limit=30
        ):
        """
        Perform hybrid search with filtering:
        1. Retrieve results using both text and image embeddings.
        2. Apply filters on gender, country, and clothing type.
        
        NOTE: Currently, the client does not support native score adjustment for multi-vector
        queries, so text_weight and image_weight are not applied automatically.
        """
        # Construct filters
        filters = []
        if master_gender_id is not None:
            filters.append(FieldCondition(key="master_gender_id", match=MatchValue(value=master_gender_id)))
        if country_id is not None:
            filters.append(FieldCondition(key="country_id", match=MatchValue(value=country_id)))
        if master_clothe_type_id is not None:
            filters.append(FieldCondition(key="master_clothe_type_id", match=MatchValue(value=master_clothe_type_id)))
        filter_obj = Filter(must=filters) if filters else None

        # Create a SearchRequest using multi-vector query.
        # The keys "text" and "image" must match the names used during upsert.
        search_request = models.SearchRequest(
            vector={"text": query_text_vector, "image": query_image_vector},
            filter=filter_obj,
            limit=limit,
            with_payload=True
        )
        
        # Use search_batch with a single SearchRequest to perform multi-vector search.
        search_results_batch = self.client.search_batch(
            collection_name=self.collection_name,
            requests=[search_request]
        )
        
        # Extract results from the single query in the batch
        if search_results_batch and len(search_results_batch) > 0:
            search_results = search_results_batch[0]
        else:
            search_results = []
        
        return [hit.id for hit in search_results]
    

    def upsert_multivector_example(self, ids: List[int], image_vectors: List[float], text_vectors: List[float]):
        """
        Upsert a point with multiple vectors using input parameters.
        
        Parameters:
        - id: Unique identifier for the point.
        - image_vector: List of floats representing the image embedding.
        - text_vector: List of floats representing the text embedding.
        - text_sparse (optional): A dictionary with keys "indices" and "values" for the sparse text vector.
            If not provided, a default sparse vector will be used.
        
        Example:
            text_sparse = {
                "indices": [1, 3, 5, 7],
                "values": [0.1, 0.2, 0.3, 0.4]
            }
            vector_manager.upsert_multivector_example(
                id=1,
                image_vector=[0.9, 0.1, 0.1, 0.2],
                text_vector=[0.4, 0.7, 0.1, 0.8, 0.1],
                text_sparse=text_sparse
            )
        """
     
        
        points = []
        for id, image, text in zip(ids,image_vectors, text_vectors):
            point = models.PointStruct(
                id=id,
                vector={
                    "image": image,
                    "text": text,
                },
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )


    def scroll(self, filter=None, offset=0,limit=20):
        result, next_page_offset = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
            offset=offset
        )
        results=[]
        for item in result:
            results.append(item.payload["post_id"])
        return results, next_page_offset

    def cosine_similarity(self,a, b):
        """Compute cosine similarity between two vectors."""
        a = np.array(a, dtype=float).flatten()
        b = np.array(b, dtype=float).flatten()
        print("Shape of a:", a.shape)  # Expect (1152,)
        print("Shape of b:", b.shape)  # Expect (1152,)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search_and_rerank(self, 
                        query_text_embedding: list, 
                        query_image_embedding: list,
                        filter_dict: dict = None,
                        limit: int = 30,page:int=0):
        
        # Build filters from the provided dictionary
        similarity_threshold=float(os.getenv("MATCH_SIMILARITY_THRESHOLD",0.5))
        filters = []
        if filter_dict:
            for k, v in filter_dict.items():
                filters.append(
                    FieldCondition(
                        key=k,
                        match=MatchValue(value=v)
                    )
                )
        # Create a Filter object if there are any filter conditions
        query_filter = Filter(must=filters) if filters else None

        # Step 1: Retrieve top candidates using text embeddings.
        text_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_text_embedding,
            query_filter=query_filter,
            limit=limit,
            offset=page * limit,
            score_threshold=similarity_threshold
        )
        
        # Step 2: Re-rank the results using image embeddings.
        # Assume that each result has a payload with an "image_embedding" field.
        results_with_score = []
        for result in text_results:
            candidate_image_embedding =deserialize_embedding(result.payload.get("image_embedding"))
            candidate_image_embedding=np.array(candidate_image_embedding)
            if candidate_image_embedding.shape==(1,1152):
                continue
                
            image_score = self.cosine_similarity(candidate_image_embedding, query_image_embedding)
            results_with_score.append({
                "result": result,
                "image_score": image_score
            })
        
        # Sort the list by image_score in descending order.
        results_with_score = sorted(results_with_score, key=lambda r: r["image_score"], reverse=True)
        results_with_score = [r["result"] for r in results_with_score]
        return results_with_score

if __name__ == "__main__":
    import os
    from blushy.utils.vector_manager import VectorManager
    from blushy.db import Label,get_session,VisitPost,ClickedItem
    from blushy.utils.base import deserialize_embedding
    os.environ["QDRANT_URL"] = "https://57bae1dd-4983-40da-8fc4-337da62dd839.us-east4-0.gcp.cloud.qdrant.io:6333"
    os.environ["QDRANT_API_KEY"] = "iiVKB5Zr8_d1GbUoLTl5-z5yHQAl4gMIpqjWbbbFWMtxfQIiZ2uLag"
        # Initialize VectorManager
    vector_manager = VectorManager(collection_name="items_new")
    session=get_session()
    label=session.query(Label).filter(Label.id==34251).first()
    embd=deserialize_embedding(label.text_embedding)
    embd_image=deserialize_embedding(label.image_embedding)
    print(vector_manager.search_and_rerank(embd,embd_image, limit=30,page=0))
    
    