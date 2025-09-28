from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import tempfile
import os
import sys
import subprocess
from pathlib import Path
import json

# Add your agents directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def convert_webm_to_mp3(webm_path: str) -> str:
    """Convert WebM audio to MP3 format for voice processing"""
    try:
        mp3_path = webm_path.replace('.webm', '.mp3')
        
        # Check if FFmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg not available - using original file")
            return webm_path
        
        print(f"Converting {webm_path} to {mp3_path}")
        
        cmd = [
            'ffmpeg', '-i', webm_path,
            '-acodec', 'libmp3lame',
            '-ar', '16000',
            '-ac', '1',
            '-ab', '128k',
            '-y',
            mp3_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(mp3_path):
            print(f"Successfully converted to {mp3_path}")
            return mp3_path
        else:
            print(f"FFmpeg conversion failed: {result.stderr}")
            return webm_path
            
    except subprocess.TimeoutExpired:
        print("FFmpeg conversion timed out")
        return webm_path
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return webm_path

def convert_webm_to_wav_python(webm_path: str) -> str:
    """Fallback: Convert WebM to WAV using Python libraries"""
    try:
        from pydub import AudioSegment
        
        wav_path = webm_path.replace('.webm', '.wav')
        print(f"Converting {webm_path} to {wav_path} using pydub")
        
        audio = AudioSegment.from_file(webm_path, format="webm")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")
        
        if os.path.exists(wav_path):
            print(f"Successfully converted to {wav_path} using pydub")
            return wav_path
        else:
            print("Pydub conversion failed")
            return webm_path
            
    except ImportError:
        print("Pydub not available - install with: pip install pydub")
        return webm_path
    except Exception as e:
        print(f"Pydub conversion error: {e}")
        return webm_path

def convert_audio_for_voice_processing(webm_path: str) -> str:
    """Convert audio to a format suitable for voice processing"""
    mp3_path = convert_webm_to_mp3(webm_path)
    if mp3_path != webm_path:
        return mp3_path
    
    wav_path = convert_webm_to_wav_python(webm_path)
    if wav_path != webm_path:
        return wav_path
    
    print("All conversion methods failed - using original WebM file")
    return webm_path

# Initialize all agents as None first
voice_auth_agent = None
llm_agent = None  
payment_agent = None

print("=== IMPORTING AGENTS ===")

# Import voice authentication agent
try:
    from voice.agent import root_agent as voice_auth_agent
    print("Voice authentication agent imported from voice.agent")
except ImportError as e:
    print(f"Voice auth import error: {e}")

# Import LLM agent
try:
    from LLMAgent.llm_agent import root_agent as llm_agent
    print("LLM agent imported successfully")
except ImportError as e:
    print(f"LLM agent import error: {e}")

# Import payment processing agent
try:
    from payment.agent import root_agent as payment_agent
    print("Payment agent imported from payment.agent")
except ImportError as e:
    print(f"Payment agent import error: {e}")

# Report agent status
print("=== AGENT STATUS ===")
print(f"Voice Auth Agent: {'LOADED' if voice_auth_agent is not None else 'NOT LOADED'}")
print(f"LLM Agent: {'LOADED' if llm_agent is not None else 'NOT LOADED'}")
print(f"Payment Agent: {'LOADED' if payment_agent is not None else 'NOT LOADED'}")
print("=== END AGENT LOADING ===\n")

# Global storage for payment context
payment_context = {}

async def process_payment_step(extracted_numbers: list, authenticated_user: str):
    """Step 4: Process the actual payment after successful authentication"""
    
    print("Step 4: Processing payment via Stripe...")
    
    if payment_agent is None:
        return {
            "success": False,
            "status": "error",
            "reason": "Payment agent not available",
            "step": "payment_processing"
        }
    
    if not payment_context:
        return {
            "success": False,
            "status": "error", 
            "reason": "No payment details found",
            "step": "payment_processing"
        }
    
    try:
        payment_details = payment_context.get("payment_details", {})
        amount = payment_details.get("amount")
        recipient = payment_details.get("recipient", "Unknown")
        currency = payment_details.get("currency", "usd")
        
        if not amount or amount <= 0:
            return {
                "success": False,
                "status": "error",
                "reason": "Invalid payment amount",
                "step": "payment_processing"
            }
        
        print(f"Processing payment: ${amount/100:.2f} to {recipient} for user {authenticated_user}")
        
        try:
            from payment.agent import process_payment_tool
            
            payment_result = await process_payment_tool(
                amount=amount,
                currency=currency,
                recipient=recipient,
                payer=authenticated_user
            )
            
            print(f"Payment processing result: {payment_result}")
            
            if payment_result.get("status") == "success":
                return {
                    "success": True,
                    "status": "success",
                    "payment_intent_id": payment_result.get("payment_intent_id"),
                    "amount": amount,
                    "currency": currency,
                    "recipient": recipient,
                    "payer": authenticated_user,
                    "formatted_amount": f"${amount/100:.2f}",
                    "step": "payment_processing",
                    "message": f"Payment of ${amount/100:.2f} to {recipient} processed successfully"
                }
            else:
                return {
                    "success": False,
                    "status": payment_result.get("status", "error"),
                    "reason": payment_result.get("reason", "Payment processing failed"),
                    "amount": amount,
                    "recipient": recipient,
                    "payer": authenticated_user,
                    "step": "payment_processing"
                }
                
        except ImportError:
            print("Could not import payment processing function")
            return {
                "success": False,
                "status": "error",
                "reason": "Payment processing function not available",
                "step": "payment_processing"
            }
            
    except Exception as payment_error:
        print(f"Payment processing error: {str(payment_error)}")
        return {
            "success": False,
            "status": "error",
            "reason": f"Payment failed: {str(payment_error)}",
            "step": "payment_processing"
        }

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class AudioRequest(BaseModel):
    audio_data: str
    audio_format: str
    sample_rate: int
    step: str = "payment"

class AudioResponse(BaseModel):
    transcript: str | None = None
    payment_analysis: dict | None = None
    voice_authentication: dict | None = None
    payment_processing: dict | None = None
    message: str
    next_step: str | None = None

@app.post("/process_voice")  
async def process_voice(audio_request: AudioRequest):
    print(f"Processing step: {audio_request.step}")
    
    try:
        audio_bytes = base64.b64decode(audio_request.audio_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            if audio_request.step == "payment":
                return await process_payment_step_handler(temp_file_path)
            elif audio_request.step == "auth":
                return await process_authentication_step(temp_file_path)
            else:
                return AudioResponse(
                    transcript=None,
                    payment_analysis=None,
                    voice_authentication=None,
                    payment_processing=None,
                    message="Invalid step specified",
                    next_step=None
                )
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return AudioResponse(
            transcript=f"Error: {str(e)}",
            payment_analysis=None,
            voice_authentication=None,
            payment_processing=None,
            message="Error processing audio",
            next_step=None
        )

async def process_payment_step_handler(temp_file_path: str):
    """Process the first recording for payment command detection"""
    
    print("Step 1: Transcribing audio...")
    
    try:
        from voiceF.agent import transcribe_voice_file
        transcribe_response = transcribe_voice_file(temp_file_path)
    except Exception as e:
        return AudioResponse(
            transcript=f"Transcription error: {str(e)}",
            payment_analysis=None,
            voice_authentication=None,
            payment_processing=None,
            message="Step 1 failed: Transcription error",
            next_step=None
        )
    
    # Parse transcription
    transcript = ""
    try:
        transcription_data = json.loads(transcribe_response)
        if transcription_data.get("success"):
            transcript = transcription_data.get("transcript", "")
        else:
            transcript = transcription_data.get("error", "Transcription failed")
    except json.JSONDecodeError:
        transcript = transcribe_response
    
    print(f"Step 1 Complete - Transcript: '{transcript}'")
    
    # Clean transcript
    clean_transcript = transcript
    if "Transcript: " in transcript:
        lines = transcript.split('\n')
        for line in lines:
            if line.startswith("Transcript: "):
                clean_transcript = line.replace("Transcript: ", "").strip()
                break
    
    # Payment Analysis
    payment_analysis = {
        "success": True,
        "has_payment_command": False,
        "payment_details": {
            "action": None,
            "amount": None,
            "currency": "usd",
            "recipient": None,
            "user_id": "USER_001",
            "raw_amount_text": None,
            "confidence": 0.0
        },
        "extracted_entities": {
            "amounts_found": [],
            "recipients_found": [],
            "actions_found": []
        },
        "reasoning": f"Manual analysis of transcript: '{clean_transcript}'",
        "transcript": clean_transcript
    }
    
    # Payment action detection
    payment_keywords = ["pay", "send", "sent", "transfer", "give", "wire", "remit"]
    transcript_lower = clean_transcript.lower()
    
    found_actions = [action for action in payment_keywords if action in transcript_lower]
    if found_actions:
        payment_analysis["has_payment_command"] = True
        payment_analysis["payment_details"]["action"] = found_actions[0]
        payment_analysis["extracted_entities"]["actions_found"] = found_actions
    
    # Amount detection
    import re
    amount_patterns = [
        r'(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?)',
        r'\$(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*(?:euros?)',
        r'(\d+(?:\.\d{2})?)\s*(?:pounds?)'
    ]
    
    amounts_found = []
    raw_amount_text = None
    for pattern in amount_patterns:
        matches = re.findall(pattern, clean_transcript, re.IGNORECASE)
        if matches:
            amounts_found.extend(matches)
            match_obj = re.search(pattern, clean_transcript, re.IGNORECASE)
            if match_obj:
                raw_amount_text = match_obj.group(0)
            break
    
    if amounts_found:
        try:
            amount_value = float(amounts_found[0])
            amount_cents = int(amount_value * 100)
            
            payment_analysis["payment_details"]["amount"] = amount_cents
            payment_analysis["payment_details"]["raw_amount_text"] = raw_amount_text or amounts_found[0]
            payment_analysis["extracted_entities"]["amounts_found"] = amounts_found
        except (ValueError, IndexError):
            pass
    
    # Recipient detection
    recipient_patterns = [
        r'(?:to|for)\s+([a-zA-Z][a-zA-Z\s]+?)(?:\s*[.,]|$)',
        r'(?:towards|at)\s+([a-zA-Z][a-zA-Z\s]+?)(?:\s*[.,]|$)'
    ]
    
    recipients_found = []
    for pattern in recipient_patterns:
        matches = re.findall(pattern, clean_transcript, re.IGNORECASE)
        for match in matches:
            clean_recipient = match.strip().title()
            if len(clean_recipient) > 1:
                recipients_found.append(clean_recipient)
    
    if recipients_found:
        payment_analysis["payment_details"]["recipient"] = recipients_found[0]
        payment_analysis["extracted_entities"]["recipients_found"] = recipients_found
    
    # Calculate confidence
    confidence_factors = []
    if found_actions:
        confidence_factors.append(0.4)
    if amounts_found:
        confidence_factors.append(0.4)
    if recipients_found:
        confidence_factors.append(0.2)
    
    final_confidence = sum(confidence_factors)
    payment_analysis["payment_details"]["confidence"] = final_confidence
    
    # Determine next step
    if payment_analysis.get("has_payment_command", False):
        # Store payment details for Step 4
        payment_context["payment_details"] = payment_analysis["payment_details"]
        payment_context["timestamp"] = json.dumps({"step2_completed": True})
        
        next_step = "auth"
        message = "Payment command detected! Please record your 5-digit PIN for authentication."
    else:
        payment_context.clear()
        next_step = "complete"
        message = "No payment command detected. Please try again with a payment instruction."
    
    return AudioResponse(
        transcript=transcript,
        payment_analysis=payment_analysis,
        voice_authentication=None,
        payment_processing=None,
        message=message,
        next_step=next_step
    )

async def process_authentication_step(temp_file_path: str):
    """Process the second recording for voice authentication"""
    
    print("Step 3: Processing voice authentication...")
    
    if voice_auth_agent is None:
        return AudioResponse(
            transcript=None,
            payment_analysis=None,
            voice_authentication={
                "success": False,
                "authenticated": False,
                "user_card_id": "0",
                "error": "Voice authentication agent not available"
            },
            payment_processing=None,
            message="Voice authentication system not available",
            next_step="complete"
        )
    
    try:
        # Convert audio for better processing
        converted_file_path = convert_audio_for_voice_processing(temp_file_path)
        print(f"Using audio file for voice processing: {converted_file_path}")
        
        # Transcribe to get spoken numbers
        try:
            from voiceF.agent import transcribe_voice_file
            transcribe_response = transcribe_voice_file(temp_file_path)
            
            transcript_data = json.loads(transcribe_response) if transcribe_response.startswith('{') else {"transcript": transcribe_response}
            spoken_text = transcript_data.get("transcript", "")
            
        except Exception as trans_error:
            spoken_text = "Transcription failed"
        
        # Extract clean transcript
        clean_transcript = spoken_text
        if "Transcript: " in spoken_text:
            lines = spoken_text.split('\n')
            for line in lines:
                if line.startswith("Transcript: "):
                    clean_transcript = line.replace("Transcript: ", "").strip()
                    break
        
        # Extract numbers from transcript
        import re
        digit_matches = re.findall(r'\b([0-9])\b', clean_transcript)
        extracted_numbers = [int(d) for d in digit_matches[:5]] if len(digit_matches) >= 5 else []
        
        payment_result = None
        
        if len(extracted_numbers) == 5:
            try:
                # PIN-only authentication for prototype
                from voice.agent import db
                import sqlite3
                
                print(f"Checking PIN {extracted_numbers} against database...")
                
                with sqlite3.connect(db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT user_id, secret_numbers FROM voice_auth 
                        WHERE is_active = 1
                    ''')
                    
                    rows = cursor.fetchall()
                    matching_user = None
                    
                    for user_id, stored_numbers_json in rows:
                        stored_numbers = json.loads(stored_numbers_json)
                        print(f"Checking user {user_id}: stored PIN {stored_numbers} vs input PIN {extracted_numbers}")
                        
                        if stored_numbers == extracted_numbers:
                            matching_user = user_id
                            print(f"PIN match found for user: {user_id}")
                            break
                    
                    if matching_user:
                        print(f"Authentication successful! Processing payment for user: {matching_user}")
                        
                        # Step 4: Process payment automatically
                        payment_result = await process_payment_step(extracted_numbers, matching_user)
                        
                        auth_result = {
                            "success": True,
                            "authenticated": True,
                            "user_card_id": matching_user,
                            "similarity_score": 1.0,
                            "message": f"Authentication successful for user {matching_user}",
                            "extracted_numbers": extracted_numbers,
                            "auth_method": "PIN_ONLY_PROTOTYPE",
                            "payment_triggered": True
                        }
                    else:
                        auth_result = {
                            "success": True,
                            "authenticated": False,
                            "user_card_id": "0",
                            "similarity_score": 0.0,
                            "message": f"Authentication failed - no user found with PIN {extracted_numbers}",
                            "extracted_numbers": extracted_numbers,
                            "auth_method": "PIN_ONLY_PROTOTYPE"
                        }
                        
            except Exception as auth_error:
                print(f"Database authentication error: {auth_error}")
                auth_result = {
                    "success": False,
                    "authenticated": False,
                    "user_card_id": "0",
                    "error": f"Database check failed: {str(auth_error)}",
                    "extracted_numbers": extracted_numbers
                }
        else:
            auth_result = {
                "success": False,
                "authenticated": False,
                "user_card_id": "0",
                "error": f"Could not extract 5 numbers. Got {len(extracted_numbers)}: {extracted_numbers}"
            }
        
        # Clean up converted file
        if converted_file_path != temp_file_path and os.path.exists(converted_file_path):
            try:
                os.unlink(converted_file_path)
            except:
                pass
        
        # Determine final message
        if auth_result.get("authenticated", False):
            if payment_result and payment_result.get("success", False):
                user_id = auth_result.get("user_card_id", "Unknown")
                amount = payment_result.get("formatted_amount", "Unknown")
                recipient = payment_result.get("recipient", "Unknown")
                message = f"Transaction completed! User {user_id} paid {amount} to {recipient}"
            elif payment_result:
                message = f"Authentication successful but payment failed: {payment_result.get('reason', 'Unknown error')}"
            else:
                user_id = auth_result.get("user_card_id", "Unknown")
                message = f"Authentication successful for user {user_id}, but payment processing was skipped"
        elif auth_result.get("success", False):
            message = f"Authentication failed - user not found with PIN {extracted_numbers}"
        else:
            error = auth_result.get("error", "Unknown error")
            message = f"Authentication error: {error}"
        
        return AudioResponse(
            transcript=None,
            payment_analysis=None,
            voice_authentication=auth_result,
            payment_processing=payment_result,
            message=message,
            next_step="complete"
        )
        
    except Exception as e:
        return AudioResponse(
            transcript=None,
            payment_analysis=None,
            voice_authentication={
                "success": False,
                "authenticated": False,
                "user_card_id": "0",
                "error": f"Processing failed: {str(e)}"
            },
            payment_processing=None,
            message=f"Authentication error: {str(e)}",
            next_step="complete"
        )

# Keep original endpoint for compatibility
@app.post("/obtain_audio")  
async def obtain_audio(audio_request: AudioRequest):
    audio_request.step = "payment"
    return await process_voice(audio_request)

@app.get("/health")
async def health_check():
    agents_status = ["transcribe"]
    if llm_agent is not None:
        agents_status.append("llm_payment")
    if voice_auth_agent is not None:
        agents_status.append("voice_auth")
    if payment_agent is not None:
        agents_status.append("payment_processing")
    
    return {"status": "healthy", "agents": agents_status}

@app.get("/")
async def root():
    return {"message": "Voice Payment API - Complete 4-Step Pipeline (Transcription + Payment Analysis + Voice Authentication + Payment Processing)"}

@app.get("/pipeline_status")
async def pipeline_status():
    """Check the status of all pipeline components"""
    return {
        "step1_transcription": {
            "available": True,
            "agent": "voiceF transcription agent"
        },
        "step2_payment_analysis": {
            "available": llm_agent is not None,
            "agent": "LLM payment analysis agent",
            "fallback": "Manual pattern matching (always available)"
        },
        "step3_voice_authentication": {
            "available": voice_auth_agent is not None,
            "agent": "Voice authentication agent",
            "mode": "PIN-only for prototype"
        },
        "step4_payment_processing": {
            "available": payment_agent is not None,
            "agent": "Stripe payment agent"
        },
        "current_payment_context": {
            "has_pending_payment": bool(payment_context),
            "details": payment_context if payment_context else None
        }
    }

@app.get("/inspect_database")
async def inspect_database():
    """Inspect the voice authentication database"""
    try:
        from voice.agent import db
        import sqlite3
        
        if not os.path.exists(db.db_path):
            return {"error": "Database file not found"}
        
        inspection_results = {
            "database_path": db.db_path,
            "users": [],
            "total_users": 0,
            "active_users": 0
        }
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, secret_numbers, created_at, is_active
                FROM voice_auth ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            inspection_results["total_users"] = len(rows)
            
            for row in rows:
                user_id, secret_numbers_json, created_at, is_active = row
                
                try:
                    secret_numbers = json.loads(secret_numbers_json)
                except:
                    secret_numbers = "Failed to decode"
                
                user_info = {
                    "user_id": user_id,
                    "secret_pin": secret_numbers,
                    "created_at": created_at,
                    "is_active": bool(is_active)
                }
                
                inspection_results["users"].append(user_info)
                
                if is_active:
                    inspection_results["active_users"] += 1
        
        return inspection_results
        
    except Exception as e:
        return {"error": f"Database inspection failed: {str(e)}"}