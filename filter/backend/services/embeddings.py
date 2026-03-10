"""Embedding service for generating text embeddings using BGE model"""
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import asyncio
from functools import partial

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model: SentenceTransformer = None
        self.dimension = 384
    
    def load_model(self) -> None:
        """Load the BGE model into memory"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✓ Model loaded successfully (dimension: {self.dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate normalized embedding for text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Run CPU-bound operation in thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                partial(self.model.encode, text, normalize_embeddings=True)
            )
            
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate normalized embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Run CPU-bound operation in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                partial(self.model.encode, texts, normalize_embeddings=True)
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    @staticmethod
    def normalize_vector(vector: List[float]) -> List[float]:
        """
        Normalize a vector to unit length (L2 norm = 1)
        
        Args:
            vector: Input vector
            
        Returns:
            Normalized vector
        """
        vec_array = np.array(vector)
        norm = np.linalg.norm(vec_array)
        if norm == 0:
            return vector
        return (vec_array / norm).tolist()


# Global embedding service instance
embedding_service = EmbeddingService()
