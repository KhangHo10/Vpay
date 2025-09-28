import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tools.voice_to_embedded import generate_100d_voice_embedding, get_audio_hash
from tools.voice_to_number import AudioProcessor
from .voice_auth_database import VoiceAuthDatabase

class VoiceAuthenticationService:
    """Complete voice authentication service that combines processing and database operations"""
    
    def __init__(self, db_path: str = "voice_auth.db", similarity_threshold: float = 0.85):
        """
        Initialize the voice authentication service
        
        Args:
            db_path: Path to SQLite database file
            similarity_threshold: Minimum similarity score for authentication (0.0 to 1.0)
        """
        self.db = VoiceAuthDatabase(db_path)
        self.audio_processor = AudioProcessor()
        self.similarity_threshold = similarity_threshold
        print(f"Voice Authentication Service initialized with threshold: {similarity_threshold}")
    
    def register_user(self, user_id: str, audio_file_path: str) -> Dict[str, Any]:
        """
        Register a new user by processing their audio file and storing in database
        
        Args:
            user_id: Unique identifier for the user (e.g., card ID)
            audio_file_path: Path to the user's audio file
            
        Returns:
            Dictionary with registration result
        """
        try:
            print(f"Registering user: {user_id} with audio: {audio_file_path}")
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_file_path}",
                    "user_id": user_id
                }
            
            # Generate voice embedding
            embedding_result = generate_100d_voice_embedding(audio_file_path)
            if not embedding_result.get("voice_embedding"):
                return {
                    "success": False,
                    "error": "Failed to generate voice embedding",
                    "user_id": user_id
                }
            
            # Extract secret numbers
            numbers_result = self.audio_processor.process_json_output(audio_file_path)
            if not numbers_result.get("numbers") or len(numbers_result["numbers"]) != 5:
                return {
                    "success": False,
                    "error": f"Failed to extract 5 secret numbers. Got: {numbers_result.get('numbers', [])}",
                    "user_id": user_id
                }
            
            # Get file hash
            file_hash = get_audio_hash(audio_file_path)
            
            # Store in database
            success = self.db.store_voice_data(
                user_id=user_id,
                voice_embedding=embedding_result["voice_embedding"],
                secret_numbers=numbers_result["numbers"],
                embedding_method=embedding_result.get("method", "audio_features"),
                file_hash=file_hash
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"User {user_id} registered successfully",
                    "user_id": user_id,
                    "embedding_dimensions": len(embedding_result["voice_embedding"]),
                    "secret_numbers_count": len(numbers_result["numbers"]),
                    "embedding_method": embedding_result.get("method"),
                    "file_hash": file_hash[:8]  # Show first 8 chars
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store data in database",
                    "user_id": user_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}",
                "user_id": user_id
            }
    
    def authenticate_user(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Authenticate a user by processing their audio and comparing with database
        
        Args:
            audio_file_path: Path to the authentication audio file
            
        Returns:
            Dictionary with authentication result including user_id or 0
        """
        try:
            print(f"Authenticating user with audio: {audio_file_path}")
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return {
                    "success": False,
                    "authenticated": False,
                    "user_id": "0",
                    "error": f"Audio file not found: {audio_file_path}",
                    "similarity_score": 0.0
                }
            
            # Generate voice embedding
            embedding_result = generate_100d_voice_embedding(audio_file_path)
            if not embedding_result.get("voice_embedding"):
                return {
                    "success": False,
                    "authenticated": False,
                    "user_id": "0",
                    "error": "Failed to generate voice embedding",
                    "similarity_score": 0.0
                }
            
            # Extract secret numbers
            numbers_result = self.audio_processor.process_json_output(audio_file_path)
            if not numbers_result.get("numbers") or len(numbers_result["numbers"]) != 5:
                return {
                    "success": False,
                    "authenticated": False,
                    "user_id": "0",
                    "error": f"Failed to extract 5 secret numbers. Got: {numbers_result.get('numbers', [])}",
                    "similarity_score": 0.0
                }
            
            # Authenticate against database
            authenticated_user_id, similarity_score = self.db.authenticate_user(
                voice_embedding=embedding_result["voice_embedding"],
                secret_numbers=numbers_result["numbers"],
                similarity_threshold=self.similarity_threshold
            )
            
            if authenticated_user_id:
                return {
                    "success": True,
                    "authenticated": True,
                    "user_id": authenticated_user_id,
                    "similarity_score": similarity_score,
                    "threshold_used": self.similarity_threshold,
                    "message": f"Authentication successful for user {authenticated_user_id}"
                }
            else:
                return {
                    "success": True,
                    "authenticated": False,
                    "user_id": "0",
                    "similarity_score": similarity_score,
                    "threshold_used": self.similarity_threshold,
                    "message": "Authentication failed - no matching user found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "authenticated": False,
                "user_id": "0",
                "error": f"Authentication failed: {str(e)}",
                "similarity_score": 0.0
            }
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get stored information for a specific user"""
        try:
            user_data = self.db.get_voice_data(user_id)
            if user_data:
                # Don't return the actual embedding and numbers for security
                return {
                    "success": True,
                    "user_id": user_data["user_id"],
                    "embedding_method": user_data["embedding_method"],
                    "created_at": user_data["created_at"],
                    "updated_at": user_data["updated_at"],
                    "is_active": user_data["is_active"],
                    "embedding_dimensions": len(user_data["voice_embedding"]),
                    "has_secret_numbers": len(user_data["secret_numbers"]) == 5
                }
            else:
                return {
                    "success": False,
                    "error": f"User {user_id} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving user info: {str(e)}"
            }
    
    def list_all_users(self) -> Dict[str, Any]:
        """List all registered users"""
        try:
            users = self.db.list_all_users()
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
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats = self.db.get_database_stats()
            stats["similarity_threshold"] = self.similarity_threshold
            stats["success"] = True
            return stats
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting stats: {str(e)}"
            }
    
    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivate a user"""
        try:
            success = self.db.deactivate_user(user_id)
            if success:
                return {
                    "success": True,
                    "message": f"User {user_id} deactivated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to deactivate user {user_id}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deactivating user: {str(e)}"
            }

# Updated agent integration functions
def register_voice_user(user_id: str, audio_file_path: str) -> Dict[str, Any]:
    """
    Register a new user for voice authentication
    
    Args:
        user_id: Unique user identifier (e.g., bank card ID)
        audio_file_path: Path to user's registration audio file
        
    Returns:
        Registration result dictionary
    """
    service = VoiceAuthenticationService()
    return service.register_user(user_id, audio_file_path)

def authenticate_voice_user(audio_file_path: str) -> Dict[str, Any]:
    """
    Authenticate a user via voice
    
    Args:
        audio_file_path: Path to authentication audio file
        
    Returns:
        Authentication result with user_id or "0" if failed
    """
    service = VoiceAuthenticationService()
    return service.authenticate_user(audio_file_path)

def get_voice_user_info(user_id: str) -> Dict[str, Any]:
    """Get information about a registered user"""
    service = VoiceAuthenticationService()
    return service.get_user_info(user_id)

def list_voice_users() -> Dict[str, Any]:
    """List all registered voice users"""
    service = VoiceAuthenticationService()
    return service.list_all_users()

def get_voice_system_stats() -> Dict[str, Any]:
    """Get voice authentication system statistics"""
    service = VoiceAuthenticationService()
    return service.get_system_stats()

# Demo and testing
def demo_complete_system():
    """Complete demonstration of the voice authentication system"""
    print("=== Complete Voice Authentication System Demo ===\n")
    
    service = VoiceAuthenticationService("demo_complete.db")
    
    # Test registration
    print("1. Registering a test user...")
    reg_result = service.register_user("CARD_12345", "../prototype/Voice1.mp3")
    print(f"Registration result: {reg_result}\n")
    
    # Test authentication with same file (should succeed)
    print("2. Testing authentication with same voice...")
    auth_result = service.authenticate_user("../prototype/Voice1.mp3")
    print(f"Authentication result: {auth_result}\n")
    
    # Test with different file (should fail)
    print("3. Testing authentication with different voice...")
    if os.path.exists("../prototype/Voice2.mp3"):
        auth_result2 = service.authenticate_user("../prototype/Voice2.mp3")
        print(f"Authentication result: {auth_result2}\n")
    
    # Show system stats
    print("4. System statistics...")
    stats = service.get_system_stats()
    print(f"Stats: {stats}\n")
    
    # List users
    print("5. All registered users...")
    users = service.list_all_users()
    print(f"Users: {users}")

if __name__ == "__main__":
    demo_complete_system()