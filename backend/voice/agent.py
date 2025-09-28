import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sqlite3
import json
import numpy as np
from datetime import datetime

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from google.adk.agents import Agent
from tools.voice_to_embedded import get_audio_hash, generate_100d_voice_embedding
from tools.voice_to_number import AudioProcessor

# Embedded database class

# This is the voice authentication agent that authenticates the user voices according 
# to different pitch, extenuation, and more
class VoiceAuthDatabase:
    def __init__(self, db_path: str = "voice_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voice_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    voice_embedding TEXT NOT NULL,
                    secret_numbers TEXT NOT NULL,
                    embedding_method TEXT DEFAULT 'audio_features',
                    file_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON voice_auth(user_id)')
            conn.commit()
    
    def store_voice_data(self, user_id: str, voice_embedding: List[float], 
                        secret_numbers: List[int], embedding_method: str = "audio_features",
                        file_hash: str = None) -> bool:
        try:
            if len(voice_embedding) != 100 or len(secret_numbers) != 5:
                return False
            
            embedding_json = json.dumps(voice_embedding)
            numbers_json = json.dumps(secret_numbers)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO voice_auth 
                    (user_id, voice_embedding, secret_numbers, embedding_method, file_hash, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, embedding_json, numbers_json, embedding_method, file_hash))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def authenticate_user(self, voice_embedding: List[float], secret_numbers: List[int], 
                         similarity_threshold: float = 0.85) -> Tuple[Optional[str], float]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, voice_embedding, secret_numbers 
                    FROM voice_auth WHERE is_active = 1
                ''')
                
                rows = cursor.fetchall()
                best_match = None
                best_similarity = 0.0
                input_embedding = np.array(voice_embedding)
                
                for row in rows:
                    user_id, stored_embedding_json, stored_numbers_json = row
                    stored_embedding = np.array(json.loads(stored_embedding_json))
                    stored_numbers = json.loads(stored_numbers_json)
                    
                    # Check if secret numbers match exactly
                    if stored_numbers != secret_numbers:
                        continue
                    
                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(input_embedding, stored_embedding)
                    
                    if similarity >= similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = user_id
                
                return best_match, best_similarity
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return None, 0.0
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, embedding_method, created_at, is_active
                    FROM voice_auth ORDER BY created_at DESC
                ''')
                rows = cursor.fetchall()
                return [
                    {
                        'user_id': row[0],
                        'embedding_method': row[1],
                        'created_at': row[2],
                        'is_active': bool(row[3])
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"List users error: {e}")
            return []
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user (soft delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE voice_auth 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"User {user_id} deactivated")
                    return True
                else:
                    print(f"User {user_id} not found or already inactive")
                    return False
                    
        except Exception as e:
            print(f"Deactivate user error: {e}")
            return False
    
    def permanently_delete_user(self, user_id: str) -> bool:
        """Permanently delete a user from database (hard delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM voice_auth WHERE user_id = ?', (user_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"User {user_id} permanently deleted")
                    return True
                else:
                    print(f"User {user_id} not found")
                    return False
                    
        except Exception as e:
            print(f"Delete user error: {e}")
            return False
    
    def reactivate_user(self, user_id: str) -> bool:
        """Reactivate a previously deactivated user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE voice_auth 
                    SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND is_active = 0
                ''', (user_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"User {user_id} reactivated")
                    return True
                else:
                    print(f"User {user_id} not found or already active")
                    return False
                    
        except Exception as e:
            print(f"Reactivate user error: {e}")
            return False
    
    def get_user_details(self, user_id: str) -> Optional[Dict]:
        """Get detailed information about a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, embedding_method, file_hash, created_at, updated_at, is_active
                    FROM voice_auth WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'embedding_method': row[1],
                        'file_hash': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'is_active': bool(row[5])
                    }
                else:
                    return None
                    
        except Exception as e:
            print(f"Get user details error: {e}")
            return None

# Global database instance
db = VoiceAuthDatabase()
audio_processor = AudioProcessor()

def process_voice_authentication(audio_file_path: str) -> Dict[str, Any]:
    """Authenticate a user by voice"""
    try:
        # Handle relative paths
        if not os.path.exists(audio_file_path) and not os.path.isabs(audio_file_path):
            prototype_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prototype", audio_file_path)
            if os.path.exists(prototype_path):
                audio_file_path = prototype_path
            else:
                return {
                    "success": False,
                    "user_card_id": "0",
                    "error": f"Audio file not found: {audio_file_path}"
                }
        
        # Generate voice embedding
        embedding_result = generate_100d_voice_embedding(audio_file_path)
        if not embedding_result.get("voice_embedding"):
            return {
                "success": False,
                "user_card_id": "0",
                "error": "Failed to generate voice embedding"
            }
        
        # Extract secret numbers
        numbers_result = audio_processor.process_json_output(audio_file_path)
        if not numbers_result.get("numbers") or len(numbers_result["numbers"]) != 5:
            return {
                "success": False,
                "user_card_id": "0",
                "error": f"Failed to extract 5 secret numbers. Got: {numbers_result.get('numbers', [])}"
            }
        
        # Authenticate against database
        authenticated_user_id, similarity_score = db.authenticate_user(
            voice_embedding=embedding_result["voice_embedding"],
            secret_numbers=numbers_result["numbers"],
            similarity_threshold=0.85
        )
        
        if authenticated_user_id:
            return {
                "success": True,
                "authenticated": True,
                "user_card_id": authenticated_user_id,
                "similarity_score": similarity_score,
                "message": f"Authentication successful for user {authenticated_user_id}"
            }
        else:
            return {
                "success": True,
                "authenticated": False,
                "user_card_id": "0",
                "similarity_score": similarity_score,
                "message": "Authentication failed - no matching user found"
            }
            
    except Exception as e:
        return {
            "success": False,
            "authenticated": False,
            "user_card_id": "0",
            "error": f"Authentication failed: {str(e)}"
        }

def register_new_user(user_card_id: str, audio_file_path: str) -> Dict[str, Any]:
    """Register a new user for voice authentication"""
    try:
        # Handle relative paths
        if not os.path.exists(audio_file_path) and not os.path.isabs(audio_file_path):
            prototype_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prototype", audio_file_path)
            if os.path.exists(prototype_path):
                audio_file_path = prototype_path
        
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file_path}",
                "user_id": user_card_id
            }
        
        # Generate voice embedding
        embedding_result = generate_100d_voice_embedding(audio_file_path)
        if not embedding_result.get("voice_embedding"):
            return {
                "success": False,
                "error": "Failed to generate voice embedding",
                "user_id": user_card_id
            }
        
        # Extract secret numbers
        numbers_result = audio_processor.process_json_output(audio_file_path)
        if not numbers_result.get("numbers") or len(numbers_result["numbers"]) != 5:
            return {
                "success": False,
                "error": f"Failed to extract 5 secret numbers. Got: {numbers_result.get('numbers', [])}",
                "user_id": user_card_id
            }
        
        # Get file hash
        file_hash = get_audio_hash(audio_file_path)
        
        # Store in database
        success = db.store_voice_data(
            user_id=user_card_id,
            voice_embedding=embedding_result["voice_embedding"],
            secret_numbers=numbers_result["numbers"],
            embedding_method=embedding_result.get("method", "audio_features"),
            file_hash=file_hash
        )
        
        if success:
            return {
                "success": True,
                "message": f"User {user_card_id} registered successfully",
                "user_id": user_card_id,
                "embedding_dimensions": len(embedding_result["voice_embedding"]),
                "secret_numbers_count": len(numbers_result["numbers"])
            }
        else:
            return {
                "success": False,
                "error": "Failed to store data in database",
                "user_id": user_card_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Registration failed: {str(e)}",
            "user_id": user_card_id
        }

def get_all_registered_users() -> Dict[str, Any]:
    """Get list of all registered users"""
    try:
        users = db.list_all_users()
        return {
            "success": True,
            "users": users,
            "total_count": len(users)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing users: {str(e)}",
            "users": []
        }

def get_system_statistics() -> Dict[str, Any]:
    """Get system statistics"""
    try:
        users = db.list_all_users()
        active_users = len([u for u in users if u['is_active']])
        db_size = os.path.getsize(db.db_path) if os.path.exists(db.db_path) else 0
        
        return {
            "success": True,
            "total_users": len(users),
            "active_users": active_users,
            "inactive_users": len(users) - active_users,
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "database_path": os.path.abspath(db.db_path),
            "similarity_threshold": 0.85
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting stats: {str(e)}"
        }

def remove_user(user_id: str, permanent: bool = False) -> Dict[str, Any]:
    """
    Remove a user from the voice authentication system
    
    Args:
        user_id: User identifier to remove
        permanent: If True, permanently delete. If False, just deactivate (default)
        
    Returns:
        Removal result dictionary
    """
    try:
        # Check if user exists first
        user_details = db.get_user_details(user_id)
        if not user_details:
            return {
                "success": False,
                "error": f"User {user_id} not found in database",
                "user_id": user_id
            }
        
        if permanent:
            # Permanent deletion
            success = db.permanently_delete_user(user_id)
            if success:
                return {
                    "success": True,
                    "message": f"User {user_id} permanently deleted from database",
                    "user_id": user_id,
                    "action": "permanent_delete",
                    "previous_status": "active" if user_details['is_active'] else "inactive"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to permanently delete user {user_id}",
                    "user_id": user_id
                }
        else:
            # Soft delete (deactivation)
            if not user_details['is_active']:
                return {
                    "success": False,
                    "error": f"User {user_id} is already inactive",
                    "user_id": user_id,
                    "current_status": "inactive"
                }
            
            success = db.deactivate_user(user_id)
            if success:
                return {
                    "success": True,
                    "message": f"User {user_id} deactivated (can be reactivated later)",
                    "user_id": user_id,
                    "action": "deactivate",
                    "note": "User data preserved - can be reactivated with reactivate_user()"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to deactivate user {user_id}",
                    "user_id": user_id
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Remove user failed: {str(e)}",
            "user_id": user_id
        }

def reactivate_user(user_id: str) -> Dict[str, Any]:
    """
    Reactivate a previously deactivated user
    
    Args:
        user_id: User identifier to reactivate
        
    Returns:
        Reactivation result dictionary
    """
    try:
        # Check if user exists
        user_details = db.get_user_details(user_id)
        if not user_details:
            return {
                "success": False,
                "error": f"User {user_id} not found in database",
                "user_id": user_id
            }
        
        if user_details['is_active']:
            return {
                "success": False,
                "error": f"User {user_id} is already active",
                "user_id": user_id,
                "current_status": "active"
            }
        
        success = db.reactivate_user(user_id)
        if success:
            return {
                "success": True,
                "message": f"User {user_id} reactivated successfully",
                "user_id": user_id,
                "action": "reactivate",
                "previous_status": "inactive",
                "current_status": "active"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to reactivate user {user_id}",
                "user_id": user_id
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Reactivate user failed: {str(e)}",
            "user_id": user_id
        }

def get_user_details(user_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific user
    
    Args:
        user_id: User identifier to lookup
        
    Returns:
        User details dictionary
    """
    try:
        user_details = db.get_user_details(user_id)
        if user_details:
            return {
                "success": True,
                "user_details": user_details,
                "user_id": user_id
            }
        else:
            return {
                "success": False,
                "error": f"User {user_id} not found",
                "user_id": user_id
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting user details: {str(e)}",
            "user_id": user_id
        }

root_agent = Agent(
    name="voice_agent",
    model="gemini-2.5-flash",
    description="Voice authentication agent with full user management capabilities including registration, authentication, and user removal",
    instruction="""
    You are a voice authentication agent with complete database management. You can:

    ## Available Functions:
    
    ### Authentication & Registration
    1. **process_voice_authentication(audio_file_path)** - Authenticate a user
       - Returns user_card_id if successful, "0" if failed
       - Requires both voice match (similarity ≥ 0.85) AND exact number match
    
    2. **register_new_user(user_card_id, audio_file_path)** - Register a new user
       - Links audio to user_card_id (bank card identifier)
       - Extracts voice embedding and 5 secret numbers

    ### User Management
    3. **remove_user(user_id, permanent=False)** - Remove a user
       - permanent=False: Deactivate user (soft delete, can be restored)
       - permanent=True: Permanently delete user (cannot be undone)
    
    4. **reactivate_user(user_id)** - Reactivate a deactivated user
       - Restores a previously deactivated user
    
    5. **get_user_details(user_id)** - Get detailed info about a specific user
    
    6. **get_all_registered_users()** - List all users (active and inactive)
    
    7. **get_system_statistics()** - Show database stats

    ## File Handling:
    - For files like "Voice1.mp3", automatically check ../prototype/ folder
    - Full paths work as-is

    ## User Removal Options:
    
    ### Soft Delete (Recommended):
    - `remove_user("CARD_12345")` or `remove_user("CARD_12345", permanent=False)`
    - User is deactivated but data preserved
    - Can be reactivated later with `reactivate_user("CARD_12345")`
    - User cannot authenticate while deactivated
    
    ### Permanent Delete (Irreversible):
    - `remove_user("CARD_12345", permanent=True)`
    - User data completely removed from database
    - Cannot be undone or restored
    - Use with caution!

    ## Example Commands:
    
    **Authentication:**
    - "authenticate Voice1.mp3" → process_voice_authentication("Voice1.mp3")
    
    **Registration:**
    - "register CARD_12345 Voice1.mp3" → register_new_user("CARD_12345", "Voice1.mp3")
    
    **User Removal:**
    - "remove user CARD_12345" → remove_user("CARD_12345", permanent=False)
    - "permanently delete user CARD_12345" → remove_user("CARD_12345", permanent=True)
    - "deactivate user CARD_12345" → remove_user("CARD_12345", permanent=False)
    
    **User Management:**
    - "reactivate user CARD_12345" → reactivate_user("CARD_12345")
    - "show user CARD_12345 details" → get_user_details("CARD_12345")
    - "list all users" → get_all_registered_users()
    - "show stats" → get_system_statistics()

    ## Safety Notes:
    - Always confirm before permanent deletion
    - Recommend soft delete (deactivation) for most cases
    - Soft deleted users show as "inactive" in user lists
    - Only active users can authenticate

    Be helpful and explain the difference between soft delete and permanent delete when users ask about removing users!
    """,
    tools=[
        process_voice_authentication,
        register_new_user,
        remove_user,
        reactivate_user,
        get_user_details,
        get_all_registered_users,
        get_system_statistics
    ]
)
# Compare both the embedding and the 5 numbers with records stored in the database.

#     Make a decision:
#     If a record matches (embedding similarity ≥ threshold and numbers match the enrolled secret), return that record’s user_card_id.
#     If no record matches, return 0