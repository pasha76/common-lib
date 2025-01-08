from qdrant_client.models import PointStruct,QueryRequest
from qdrant_client.models import Distance, VectorParams,MatchValue,Filter,FieldCondition
from qdrant_client import QdrantClient, models
import os
from typing import List, Dict, Union, Optional

class VectorManager:
    def __init__(self,collection_name="vendors", vector_size=768, distance=Distance.COSINE):
        url= os.getenv('QDRANT_URL')
        api_key= os.getenv('QDRANT_API_KEY')
        self.client = QdrantClient(url=url,api_key=api_key,timeout=10)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance


    def create_index(self,collection_name,field_name,field_schema):
        self.client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=field_schema)

    def recreate_collection(self):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=self.distance),
        )

    def update_metadata(self, idx,metadata):
        self.client.set_payload(
        collection_name=self.collection_name,
        payload=metadata,
        points=idx,
        )
        

    def upsert_vectors(self, idx,vectors, metadata_list=None):
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
            for idx, vector, metadata in zip(idx,vectors, metadata_list)
        ]
     
        # Note: Consider handling large batches in smaller chunks to avoid hitting server limits
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def recommend(self, positive_label_ids,negative_label_ids, user_id=None,master_gender_id=1,country_id=1, limit=10,page=0):
        return self.client.recommend(
        collection_name="posts",
        positive=positive_label_ids,
        negative=negative_label_ids,
        strategy=models.RecommendStrategy.BEST_SCORE,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="master_gender_id",
                    match=models.MatchValue(
                        value=master_gender_id,
                    ),
                
                ),
                models.FieldCondition(
                    key="country_id",
                    match=models.MatchValue(
                        value=country_id,
                    ),
                
                ),

                models.FieldCondition(
                    key="similarity_score",
                    range=models.Range(
                        gte=0.3,
                    ),
                
                ),

            ],
            must_not=[
                models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(
                            value=user_id
                        )
                    ),

                ]
            ),
            limit=limit,
            offset=page*limit
        )
    
    def search_by_batch(self,query_vectors):
        search_queries = [
            QueryRequest(query=qv)
            for qv in query_vectors
        ]
        assert len(search_queries)==len(query_vectors)

        return self.client.query_batch_points(collection_name=self.collection_name, requests=search_queries)




    def search_vectors(self, query_vector, filter=None,page=0,limit=20):
        filters=[]
        if filter:
            
            for k,v in filter.items():
                filters.append(FieldCondition(
                        key=k,
                        match=MatchValue(
                            value=v,
                        ),
                        
                    ))
        
            
        filter=Filter(must=filters)
        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter,
            limit=limit,
            offset=page*limit,
            score_threshold=None,
        )
        return result
    

    def search_from_vendor(self, query_vector, filter=None, page=0,limit=20):
        if filter:
            filter=Filter(
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
            offset=page*limit,
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

    def delete_by_filters(self,delete_filter):
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

    def batch_search_vector_with_fitlers(self, query_vectors, filter=None, limit=20, page=0):
            """
            Perform batch search for multiple query vectors with optional filtering
            """
            filters = []
            if filter:
                for k, v in filter:
                    filters.append(models.FieldCondition(
                        key=k,
                        match=models.MatchValue(
                            value=v,
                        ),
                    ))
            
            filter_obj = models.Filter(should=filters) if filters else None
            
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