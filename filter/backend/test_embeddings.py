"""Test script to verify embedding service functionality"""
import asyncio
import logging
import time
import numpy as np
from services.embeddings import embedding_service
from utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def test_embedding_service():
    """Test embedding service functionality"""
    try:
        logger.info("=" * 60)
        logger.info("Testing Embedding Service")
        logger.info("=" * 60)
        
        # Test 1: Load model
        logger.info("\n1. Testing model loading...")
        embedding_service.load_model()
        logger.info("✓ Model loaded successfully")
        
        # Test 2: Generate single embedding
        logger.info("\n2. Testing single embedding generation...")
        test_text = "Python developer with 5 years of experience in machine learning and web development"
        
        start_time = time.time()
        embedding = await embedding_service.generate_embedding(test_text)
        duration = time.time() - start_time
        
        logger.info(f"✓ Embedding generated in {duration:.3f}s")
        logger.info(f"  - Dimension: {len(embedding)}")
        logger.info(f"  - First 5 values: {embedding[:5]}")
        
        # Test 3: Verify dimension
        logger.info("\n3. Testing embedding dimension...")
        assert len(embedding) == 384, f"Expected dimension 384, got {len(embedding)}"
        logger.info("✓ Dimension is correct (384)")
        
        # Test 4: Verify normalization
        logger.info("\n4. Testing embedding normalization...")
        norm = np.linalg.norm(embedding)
        logger.info(f"  - L2 norm: {norm:.6f}")
        assert abs(norm - 1.0) < 0.001, f"Expected norm ~1.0, got {norm}"
        logger.info("✓ Embedding is normalized (L2 norm ≈ 1.0)")
        
        # Test 5: Generate batch embeddings
        logger.info("\n5. Testing batch embedding generation...")
        test_texts = [
            "Senior software engineer with expertise in Python and JavaScript",
            "Data scientist specializing in deep learning and NLP",
            "Full-stack developer proficient in React and Node.js"
        ]
        
        start_time = time.time()
        batch_embeddings = await embedding_service.generate_embeddings_batch(test_texts)
        duration = time.time() - start_time
        
        logger.info(f"✓ Batch embeddings generated in {duration:.3f}s")
        logger.info(f"  - Number of embeddings: {len(batch_embeddings)}")
        logger.info(f"  - Average time per embedding: {duration/len(test_texts):.3f}s")
        
        # Test 6: Verify all batch embeddings
        logger.info("\n6. Testing batch embedding properties...")
        for i, emb in enumerate(batch_embeddings):
            assert len(emb) == 384, f"Embedding {i} has wrong dimension"
            norm = np.linalg.norm(emb)
            assert abs(norm - 1.0) < 0.001, f"Embedding {i} not normalized"
        logger.info("✓ All batch embeddings have correct dimension and normalization")
        
        # Test 7: Test similarity calculation
        logger.info("\n7. Testing similarity calculation...")
        emb1 = await embedding_service.generate_embedding("Python developer")
        emb2 = await embedding_service.generate_embedding("Python programmer")
        emb3 = await embedding_service.generate_embedding("Chef cooking pasta")
        
        # Calculate cosine similarity (dot product of normalized vectors)
        similarity_similar = np.dot(emb1, emb2)
        similarity_different = np.dot(emb1, emb3)
        
        logger.info(f"  - Similarity (Python developer vs Python programmer): {similarity_similar:.4f}")
        logger.info(f"  - Similarity (Python developer vs Chef cooking): {similarity_different:.4f}")
        
        assert similarity_similar > similarity_different, "Similar texts should have higher similarity"
        logger.info("✓ Similarity calculation works correctly")
        
        # Test 8: Test normalize_vector utility
        logger.info("\n8. Testing vector normalization utility...")
        test_vector = [3.0, 4.0, 0.0]  # Length = 5
        normalized = embedding_service.normalize_vector(test_vector)
        norm = np.linalg.norm(normalized)
        logger.info(f"  - Original vector: {test_vector}")
        logger.info(f"  - Normalized vector: {normalized}")
        logger.info(f"  - L2 norm: {norm:.6f}")
        assert abs(norm - 1.0) < 0.001, "Normalized vector should have norm 1.0"
        logger.info("✓ Vector normalization utility works correctly")
        
        # Test 9: Test empty text handling
        logger.info("\n9. Testing edge cases...")
        try:
            empty_embedding = await embedding_service.generate_embedding("")
            logger.info(f"  - Empty text embedding dimension: {len(empty_embedding)}")
            logger.info("✓ Empty text handled gracefully")
        except Exception as e:
            logger.warning(f"  - Empty text raised exception: {e}")
        
        # Test 10: Test long text
        long_text = "Python developer " * 100  # Very long text
        long_embedding = await embedding_service.generate_embedding(long_text)
        logger.info(f"  - Long text embedding dimension: {len(long_embedding)}")
        logger.info("✓ Long text handled correctly")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All embedding service tests passed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Embedding service test failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(test_embedding_service())
