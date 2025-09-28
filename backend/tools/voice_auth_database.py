import sqlite3
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime
import hashlib

class VoiceAuthDatabase:
    def __init__(self, db_path: str = "voice_auth.db"):
        """Initialize the voice authentication database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create the main voice authentication table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voice_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    voice_embedding TEXT NOT NULL,  -- JSON array of 100 floats
                    secret_numbers TEXT NOT NULL,   -- JSON array of 5 integers
                    embedding_method TEXT DEFAULT 'audio_features',
                    file_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id ON voice_auth(user_id)
            ''')
            
            # Create index for active records
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_active ON voice_auth(is_active)
            ''')
            
            conn.commit()
            print(f"Database initialized at: {os.path.abspath(self.db_path)}")
    
    def store_voice_data(self, user_id: str, voice_embedding: List[float], 
                        secret_numbers: List[int], embedding_method: str = "audio_features",
                        file_hash: str = None) -> bool:
        """
        Store voice authentication data for a user
        
        Args:
            user_id: Unique identifier for the user (links to bank card)
            voice_embedding: List of 100 float values
            secret_numbers: List of 5 integers
            embedding_method: Method used to generate embedding
            file_hash: Hash of the original audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input
            if len(voice_embedding) != 100:
                raise ValueError(f"Voice embedding must be exactly 100 dimensions, got {len(voice_embedding)}")
            
            if len(secret_numbers) != 5:
                raise ValueError(f"Secret numbers must be exactly 5 numbers, got {len(secret_numbers)}")
            
            # Convert to JSON strings
            embedding_json = json.dumps(voice_embedding)
            numbers_json = json.dumps(secret_numbers)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or replace (upsert)
                cursor.execute('''
                    INSERT OR REPLACE INTO voice_auth 
                    (user_id, voice_embedding, secret_numbers, embedding_method, file_hash, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, embedding_json, numbers_json, embedding_method, file_hash))
                
                conn.commit()
                print(f"✅ Voice data stored for user: {user_id}")
                return True
                
        except Exception as e:
            print(f"❌ Error storing voice data: {e}")
            return False
    
    def get_voice_data(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve voice authentication data for a user
        
        Args:
            user_id: User identifier to lookup
            
        Returns:
            Dictionary with voice data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, voice_embedding, secret_numbers, embedding_method, 
                           file_hash, created_at, updated_at, is_active
                    FROM voice_auth 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'user_id': row[0],
                        'voice_embedding': json.loads(row[1]),
                        'secret_numbers': json.loads(row[2]),
                        'embedding_method': row[3],
                        'file_hash': row[4],
                        'created_at': row[5],
                        'updated_at': row[6],
                        'is_active': bool(row[7])
                    }
                else:
                    return None
                    
        except Exception as e:
            print(f"❌ Error retrieving voice data: {e}")
            return None
    
    def authenticate_user(self, voice_embedding: List[float], secret_numbers: List[int], 
                         similarity_threshold: float = 0.85) -> Tuple[Optional[str], float]:
        """
        Authenticate a user by comparing voice embedding and secret numbers
        
        Args:
            voice_embedding: 100-dimensional embedding to compare
            secret_numbers: 5 secret numbers to verify
            similarity_threshold: Minimum cosine similarity required
            
        Returns:
            Tuple of (user_id if authenticated, similarity_score) or (None, 0.0)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all active voice records
                cursor.execute('''
                    SELECT user_id, voice_embedding, secret_numbers 
                    FROM voice_auth 
                    WHERE is_active = 1
                ''')
                
                rows = cursor.fetchall()
                
                best_match = None
                best_similarity = 0.0
                
                input_embedding = np.array(voice_embedding)
                
                for row in rows:
                    user_id, stored_embedding_json, stored_numbers_json = row
                    
                    # Parse stored data
                    stored_embedding = np.array(json.loads(stored_embedding_json))
                    stored_numbers = json.loads(stored_numbers_json)
                    
                    # Check if secret numbers match exactly
                    if stored_numbers != secret_numbers:
                        continue
                    
                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(input_embedding, stored_embedding)
                    
                    # Check if this is the best match so far
                    if similarity >= similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = user_id
                
                return best_match, best_similarity
                
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return None, 0.0
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        except:
            return 0.0
    
    def list_all_users(self) -> List[Dict]:
        """Get a list of all registered users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, embedding_method, created_at, updated_at, is_active
                    FROM voice_auth 
                    ORDER BY created_at DESC
                ''')
                
                rows = cursor.fetchall()
                
                return [
                    {
                        'user_id': row[0],
                        'embedding_method': row[1],
                        'created_at': row[2],
                        'updated_at': row[3],
                        'is_active': bool(row[4])
                    }
                    for row in rows
                ]
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user's voice authentication (soft delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE voice_auth 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✅ User {user_id} deactivated")
                    return True
                else:
                    print(f"❌ User {user_id} not found")
                    return False
                    
        except Exception as e:
            print(f"❌ Error deactivating user: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count total users
                cursor.execute('SELECT COUNT(*) FROM voice_auth')
                total_users = cursor.fetchone()[0]
                
                # Count active users
                cursor.execute('SELECT COUNT(*) FROM voice_auth WHERE is_active = 1')
                active_users = cursor.fetchone()[0]
                
                # Get database file size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'database_path': os.path.abspath(self.db_path)
                }
                
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

# Example usage and testing functions
def demo_usage():
    """Demonstrate how to use the VoiceAuthDatabase"""
    
    # Initialize database
    db = VoiceAuthDatabase("demo_voice_auth.db")
    
    # Example data (you would get this from your voice processing functions)
    user_id = "CARD_12345"
    voice_embedding = [0.123] * 100  # 100 random values (replace with real embedding)
    secret_numbers = [7, 42, 13, 89, 5]
    
    print("=== Voice Authentication Database Demo ===\n")
    
    # Store voice data
    print("1. Storing voice data...")
    success = db.store_voice_data(user_id, voice_embedding, secret_numbers, file_hash="abc123")
    
    # Retrieve voice data
    print("\n2. Retrieving voice data...")
    user_data = db.get_voice_data(user_id)
    if user_data:
        print(f"Found user: {user_data['user_id']}")
        print(f"Secret numbers: {user_data['secret_numbers']}")
        print(f"Embedding dimensions: {len(user_data['voice_embedding'])}")
    
    # Test authentication
    print("\n3. Testing authentication...")
    authenticated_user, similarity = db.authenticate_user(voice_embedding, secret_numbers)
    if authenticated_user:
        print(f"✅ Authentication successful! User: {authenticated_user}")
        print(f"Similarity score: {similarity:.4f}")
    else:
        print("❌ Authentication failed")
    
    # Test with wrong numbers
    print("\n4. Testing with wrong secret numbers...")
    wrong_numbers = [1, 2, 3, 4, 5]
    authenticated_user, similarity = db.authenticate_user(voice_embedding, wrong_numbers)
    if authenticated_user:
        print(f"✅ Authentication successful! User: {authenticated_user}")
    else:
        print("❌ Authentication failed (as expected)")
    
    # Database stats
    print("\n5. Database statistics...")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # List all users
    print("\n6. All registered users...")
    users = db.list_all_users()
    for user in users:
        print(f"User: {user['user_id']}, Active: {user['is_active']}")

if __name__ == "__main__":
    demo_usage()