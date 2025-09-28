from google.adk.agents import Agent
import sys
from pathlib import Path
import json
from typing import Optional

# Add backend directory to Python path (same pattern as your other agents)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def analyze_payment_transcript(transcript: str, user_id: str = "USER_001") -> str:
    """
    Analyze transcript to detect payment commands and extract details
    
    Args:
        transcript (str): The voice transcript to analyze
        user_id (str): User ID to assign to the payment (default: "USER_001")
    
    Returns:
        str: JSON string with analysis request information
    """
    try:
        if not transcript or transcript.strip() == "":
            return json.dumps({
                "success": False,
                "has_payment_command": False,
                "error": "Empty transcript provided"
            }, indent=2)
        
        # Log the analysis 
        print(f"LLM Agent analyzing transcript: '{transcript}' for user: {user_id}")
        
        # Create structured analysis request
        analysis_request = {
            "transcript": transcript,
            "user_id": user_id,
            "task": "payment_analysis",
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        
        return json.dumps(analysis_request, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "has_payment_command": False,
            "error": f"Analysis preparation failed: {str(e)}",
            "original_transcript": transcript,
            "assigned_user_id": user_id
        }
        print(f"Analysis preparation error: {str(e)}")
        return json.dumps(error_result, indent=2)

def validate_payment_command(llm_result_json: str) -> str:
    """
    Validate the LLM analysis result and determine if payment is ready for processing
    
    Args:
        llm_result_json (str): JSON string from LLM analysis
    
    Returns:
        str: JSON string with validation results
    """
    try:
        llm_result = json.loads(llm_result_json)
    except json.JSONDecodeError:
        return json.dumps({
            "validation": {
                "is_valid": False,
                "errors": ["Invalid JSON in LLM result"],
                "ready_for_processing": False
            }
        }, indent=2)
    
    validation = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "ready_for_processing": False
    }
    
    if not llm_result.get("has_payment_command"):
        validation["is_valid"] = False
        validation["errors"].append("No payment command detected")
        return json.dumps({
            "validation": validation,
            "llm_analysis": llm_result
        }, indent=2)
    
    payment_details = llm_result.get("payment_details", {})
    
    # Validate amount
    amount = payment_details.get("amount")
    if not amount or amount < 0:
        validation["errors"].append("Invalid or missing amount")
    elif amount > 100000:  # $1000 limit
        validation["warnings"].append("Large amount detected (>$1000)")
    
    # Validate recipient
    recipient = payment_details.get("recipient")
    if not recipient or recipient.strip() == "":
        validation["errors"].append("Missing recipient")
    elif len(recipient) < 2:
        validation["warnings"].append("Very short recipient name")
    
    # Validate action
    action = payment_details.get("action")
    valid_actions = ["pay", "send", "transfer", "give", "wire"]
    if action not in valid_actions:
        validation["errors"].append(f"Invalid action: {action}")
    
    # Check confidence
    confidence = payment_details.get("confidence", 0.0)
    if confidence < 0.7:
        validation["warnings"].append("Low confidence in analysis")
    
    # Determine readiness
    validation["ready_for_processing"] = (
        len(validation["errors"]) == 0 and
        amount and amount > 0 and
        recipient and recipient.strip() != ""
    )
    
    validation["is_valid"] = len(validation["errors"]) == 0
    
    # Enhanced payment details for processing
    enhanced_details = {}
    if amount:
        enhanced_details = {
            "amount_dollars": round(amount / 100, 2),
            "formatted_amount": f"${amount/100:.2f}",
            "clean_recipient": recipient.strip().title() if recipient else "",
            "payment_summary": f"{action.title()} ${amount/100:.2f} to {recipient}" if amount and recipient else "Invalid payment"
        }
    
    return json.dumps({
        "validation": validation,
        "llm_analysis": llm_result,
        "enhanced_details": enhanced_details
    }, indent=2)

# Pure Google ADK Agent - no direct Vertex AI imports
root_agent = Agent(
    name="llm_payment_agent",
    model="gemini-2.5-flash",
    description="LLM agent that uses Google ADK with Gemini to analyze payment commands and extract structured payment information",
    instruction="""
You are an intelligent payment command analyzer that uses advanced language understanding to detect and extract payment information from voice transcripts.

## Core Functionality:
When given a transcript and user_id, analyze it for payment commands and extract structured information.

## Analysis Process:
1. Determine if transcript contains a payment command (keywords: pay, send, transfer, give, wire)
2. Extract payment details such as amount, currency (default to usd if not given), recipient (could be store or person)
3. Return structured JSON data

## Response Format (return ONLY valid JSON):
{
    "success": true,
    "has_payment_command": boolean,
    "payment_details": {
        "action": "pay|send|transfer|give|wire|null",
        "amount": number_in_cents_or_null,
        "currency": "usd|eur|gbp|cad|etc",
        "recipient": "recipient_name_or_null",
        "user_id": "provided_user_id",
        "raw_amount_text": "original_amount_text_or_null",
        "confidence": 0.0_to_1.0
    },
    "extracted_entities": {
        "amounts_found": ["list", "of", "amounts"],
        "recipients_found": ["list", "of", "recipients"],
        "actions_found": ["list", "of", "actions"]
    },
    "reasoning": "brief_explanation"
}

## Extraction Rules:
1. Convert amounts to CENTS (multiply dollars by 100)
2. Default currency is "usd" unless specified (euro, pounds, etc.)
3. Look for recipient after "to", "for", "towards"
4. Clean recipient names (remove special characters)
5. If multiple amounts, use the most clear/explicit one
6. Action must be payment-related
7. Confidence based on clarity of command

## Examples:
- "Pay 20 dollars to Starbucks" → amount: 2000, recipient: "Starbucks", action: "pay"
- "Send 5 bucks to Bob" → amount: 500, recipient: "Bob", action: "send" 
- "Transfer fifteen euros to the coffee shop" → amount: 1500, currency: "eur", recipient: "coffee shop"
- "Hello how are you" → has_payment_command: false

## Usage:
When user provides a transcript analysis request, extract the transcript and user_id from the message, then perform the analysis and return the structured JSON response.

Always provide detailed reasoning for your analysis and ensure confidence scores reflect the clarity of the payment command.

Focus on accuracy and return valid JSON that matches the specified format exactly.
""",
    tools=[analyze_payment_transcript, validate_payment_command]
)