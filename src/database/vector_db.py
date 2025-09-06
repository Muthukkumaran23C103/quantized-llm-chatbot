import sqlite3
import sqlite_vec
import os
import json
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structured search result"""
    document_id: int
    filename: str
    content: str
    metadata: Dict[str, Any]
    distance: float
    similarity_score: float

class EnhancedVectorDatabase:
    """Enhanced vector database with real semantic search capabilities"""
    
    def __init__(self, db_path: str = "data/chatbot.db"):
        self.db_path = db_path
        self.embedding_dimension = 384  # MiniLM-L6-v2 dimensions
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.connection = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize SQLite database with vector extension and enhanced schema"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            
            # Enable sqlite-vec extension
            self.connection.enable_load_extension(True)
            sqlite_vec.load(self.connection)
            self.connection.enable_load_extension(False)
            
            # Create enhanced tables
            self.create_enhanced_tables()
            
            logger.info("Enhanced vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise
    
    def create_enhanced_tables(self):
        """Create enhanced database tables with better schema"""
        cursor = self.connection.cursor()
        
        # Enhanced documents table with more metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                cleaned_content TEXT,
                content_type TEXT DEFAULT 'text',
                tokens TEXT,
                entities TEXT,
                keywords TEXT,
                word_count INTEGER,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Enhanced vector embeddings table using vec0
        cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_embeddings 
            USING vec0(
                document_id INTEGER PRIMARY KEY,
                embedding FLOAT[{self.embedding_dimension}]
            )
        """)
        
        # Chat history with embeddings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                user_embedding BLOB,
                bot_embedding BLOB,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context_documents TEXT
            )
        """)
        
        # Semantic search queries log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                query_embedding BLOB,
                results_count INTEGER,
                top_result_distance REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_queries(timestamp)")
        
        self.connection.commit()
    
    def add_document_with_embeddings(self, 
                                   filename: str, 
                                   content: str, 
                                   processed_data: Dict[str, Any],
                                   embedding: np.ndarray,
                                   metadata: Optional[Dict[str, Any]] = None) -> int:
        """Add document with full NLP processing results and embeddings"""
        cursor = self.connection.cursor()
        
        try:
            # Insert document with enhanced data
            cursor.execute("""
                INSERT INTO documents 
                (filename, content, cleaned_content, tokens, entities, keywords, 
                 word_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filename,
                content,
                processed_data.get('cleaned_content', content),
                json.dumps(processed_data.get('tokens', [])),
                json.dumps(processed_data.get('entities', [])),
                json.dumps(processed_data.get('keywords', [])),
                processed_data.get('word_count', len(content.split())),
                json.dumps(metadata) if metadata else None
            ))
            
            document_id = cursor.lastrowid
            
            # Insert embedding
            cursor.execute("""
                INSERT INTO document_embeddings (document_id, embedding)
                VALUES (?, ?)
            """, (document_id, embedding.tobytes()))
            
            self.connection.commit()
            logger.info(f"Added document {filename} with ID {document_id}")
            return document_id
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error adding document: {e}")
            raise
    
    def semantic_search(self, 
                       query_embedding: np.ndarray, 
                       limit: int = 5,
                       distance_threshold: float = 1.5) -> List[SearchResult]:
        """Perform semantic search using vector similarity"""
        cursor = self.connection.cursor()
        
        try:
            # Log search query
            self._log_search_query(query_embedding, limit)
            
            # Perform vector similarity search
            result = cursor.execute("""
                SELECT 
                    d.id,
                    d.filename,
                    d.content,
                    d.cleaned_content,
                    d.metadata,
                    e.distance
                FROM document_embeddings e
                JOIN documents d ON e.document_id = d.id
                WHERE e.embedding MATCH ? AND e.distance < ?
                ORDER BY e.distance
                LIMIT ?
            """, (query_embedding.tobytes(), distance_threshold, limit))
            
            results = []
            for row in result.fetchall():
                doc_id, filename, content, cleaned_content, metadata_json, distance = row
                
                # Parse metadata
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # Calculate similarity score (1 - normalized distance)
                similarity_score = max(0.0, 1.0 - distance)
                
                results.append(SearchResult(
                    document_id=doc_id,
                    filename=filename,
                    content=content,
                    metadata=metadata,
                    distance=distance,
                    similarity_score=similarity_score
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []
    
    def _log_search_query(self, query_embedding: np.ndarray, expected_results: int):
        """Log search queries for analytics"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO search_queries (query_embedding, results_count)
                VALUES (?, ?)
            """, (query_embedding.tobytes(), expected_results))
            self.connection.commit()
        except Exception as e:
            logger.warning(f"Could not log search query: {e}")
    
    def add_chat_with_embeddings(self, 
                                user_message: str, 
                                bot_response: str,
                                user_embedding: np.ndarray,
                                bot_embedding: np.ndarray,
                                session_id: str = None,
                                context_documents: List[int] = None):
        """Store chat with embeddings and context information"""
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO chat_history 
                (user_message, bot_response, user_embedding, bot_embedding, 
                 session_id, context_documents)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_message,
                bot_response,
                user_embedding.tobytes(),
                bot_embedding.tobytes(),
                session_id,
                json.dumps(context_documents) if context_documents else None
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error storing chat with embeddings: {e}")
            raise
    
    def get_similar_conversations(self, 
                                 query_embedding: np.ndarray, 
                                 limit: int = 3) -> List[Tuple]:
        """Find similar past conversations for context"""
        cursor = self.connection.cursor()
        
        try:
            # This is a simplified approach - in production you'd want to use
            # a proper vector similarity search for chat history too
            result = cursor.execute("""
                SELECT user_message, bot_response, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit * 3,))  # Get more results to filter
            
            conversations = result.fetchall()
            
            # For now, return recent conversations
            # TODO: Implement proper vector similarity for chat history
            return conversations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting similar conversations: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.connection.cursor()
        
        try:
            stats = {}
            
            # Document count
            result = cursor.execute("SELECT COUNT(*) FROM documents").fetchone()
            stats['document_count'] = result[0]
            
            # Embedding count
            result = cursor.execute("SELECT COUNT(*) FROM document_embeddings").fetchone()
            stats['embedding_count'] = result[0]
            
            # Chat history count
            result = cursor.execute("SELECT COUNT(*) FROM chat_history").fetchone()
            stats['chat_count'] = result[0]
            
            # Search queries count
            result = cursor.execute("SELECT COUNT(*) FROM search_queries").fetchone()
            stats['search_count'] = result[0]
            
            # Recent activity
            result = cursor.execute("""
                SELECT COUNT(*) FROM search_queries 
                WHERE timestamp > datetime('now', '-24 hours')
            """).fetchone()
            stats['searches_24h'] = result[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Test the enhanced database
if __name__ == "__main__":
    import numpy as np
    
    db = EnhancedVectorDatabase()
    
    # Test data
    test_embedding = np.random.rand(384).astype(np.float32)
    
    # Add test document
    doc_id = db.add_document_with_embeddings(
        filename="test.txt",
        content="This is a test document about Docker containerization.",
        processed_data={
            'cleaned_content': "test document Docker containerization",
            'tokens': ['test', 'document', 'docker', 'containerization'],
            'entities': [{'text': 'Docker', 'label': 'ORG'}],
            'keywords': ['docker', 'containerization', 'test'],
            'word_count': 8
        },
        embedding=test_embedding,
        metadata={'type': 'test', 'source': 'manual'}
    )
    
    print(f"Added document with ID: {doc_id}")
    
    # Test search
    search_results = db.semantic_search(test_embedding, limit=5)
    print(f"Found {len(search_results)} results")
    
    # Get stats
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
    
    db.close()
