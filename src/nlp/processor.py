import spacy
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProcessedText:
    """Structured representation of processed text"""
    original_text: str
    cleaned_text: str
    tokens: List[str]
    entities: List[Dict[str, str]]
    embeddings: np.ndarray
    sentences: List[str]

class NLPProcessor:
    """Advanced NLP processing pipeline for text preprocessing and embedding generation"""
    
    def __init__(self, 
                 spacy_model: str = "en_core_web_sm",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize NLP processor with spaCy and sentence transformer models
        
        Args:
            spacy_model: spaCy model name for preprocessing
            embedding_model: Sentence transformer model for embeddings
        """
        self.spacy_model_name = spacy_model
        self.embedding_model_name = embedding_model
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load spaCy and sentence transformer models"""
        try:
            # Load spaCy model
            logger.info(f"Loading spaCy model: {self.spacy_model_name}")
            self.nlp = spacy.load(self.spacy_model_name)
            
            # Load sentence transformer model
            logger.info(f"Loading sentence transformer: {self.embedding_model_name}")
            self.embedder = SentenceTransformer(self.embedding_model_name)
            
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading NLP models: {e}")
            raise
    
    def preprocess_text(self, text: str) -> ProcessedText:
        """
        Comprehensive text preprocessing using spaCy
        
        Args:
            text: Input text to process
            
        Returns:
            ProcessedText object with preprocessing results
        """
        try:
            # Process with spaCy
            doc = self.nlp(text)
            
            # Clean text (remove extra whitespace, normalize)
            cleaned_text = " ".join(text.split())
            
            # Extract tokens (lemmatized, filtered)
            tokens = [
                token.lemma_.lower() 
                for token in doc 
                if not token.is_stop 
                and not token.is_punct 
                and not token.is_space
                and len(token.text) > 2
            ]
            
            # Extract named entities
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "description": spacy.explain(ent.label_),
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]
            
            # Extract sentences
            sentences = [sent.text.strip() for sent in doc.sents]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(cleaned_text)
            
            return ProcessedText(
                original_text=text,
                cleaned_text=cleaned_text,
                tokens=tokens,
                entities=entities,
                embeddings=embeddings,
                sentences=sentences
            )
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            # Return minimal processed text on error
            embeddings = self.generate_embeddings(text)
            return ProcessedText(
                original_text=text,
                cleaned_text=text,
                tokens=[],
                entities=[],
                embeddings=embeddings,
                sentences=[text]
            )
    
    def generate_embeddings(self, text: str) -> np.ndarray:
        """
        Generate semantic embeddings for text
        
        Args:
            text: Input text
            
        Returns:
            numpy array of embeddings
        """
        try:
            embeddings = self.embedder.encode([text])[0]
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return zero vector on error
            return np.zeros(384, dtype=np.float32)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding arrays
        """
        try:
            embeddings = self.embedder.encode(texts)
            return [emb.astype(np.float32) for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [np.zeros(384, dtype=np.float32) for _ in texts]
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract important keywords from text using NER and POS tagging
        
        Args:
            text: Input text
            top_k: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        try:
            doc = self.nlp(text)
            
            # Extract keywords based on POS tags and entities
            keywords = []
            
            # Add named entities
            keywords.extend([ent.text.lower() for ent in doc.ents])
            
            # Add important nouns, adjectives, and verbs
            keywords.extend([
                token.lemma_.lower() 
                for token in doc 
                if token.pos_ in ['NOUN', 'ADJ', 'VERB']
                and not token.is_stop 
                and not token.is_punct
                and len(token.text) > 2
            ])
            
            # Remove duplicates and return top_k
            unique_keywords = list(set(keywords))
            return unique_keywords[:top_k]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            embeddings = self.embedder.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

# Test the NLP processor
if __name__ == "__main__":
    processor = NLPProcessor()
    
    test_text = "Docker is a containerization platform that helps developers build, ship, and run applications efficiently."
    
    result = processor.preprocess_text(test_text)
    
    print(f"Original: {result.original_text}")
    print(f"Cleaned: {result.cleaned_text}")
    print(f"Tokens: {result.tokens}")
    print(f"Entities: {result.entities}")
    print(f"Embedding shape: {result.embeddings.shape}")
    print(f"Keywords: {processor.extract_keywords(test_text)}")
