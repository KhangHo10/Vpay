from google.adk.agents import Agent
import sys
from pathlib import Path
import json

# Add backend directory to Python path
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
    instruction = """
    You are a strict payment command analyzer that extracts payment information from voice transcripts with exact JSON formatting.

    ## CRITICAL: Response Format Requirements
    You MUST return ONLY valid JSON in this EXACT structure (no additional text, explanations, or markdown):

    {
        "success": boolean,
        "has_payment_command": boolean,
        "recipients": string_or_null,
        "action": string_or_null,
        "amounts": number_or_null,
        "currency": string
    }

    ## Field Specifications:

    ### success (boolean)
    - true: Analysis completed successfully
    - false: Unable to process transcript

    ### has_payment_command (boolean)  
    - true: Transcript contains clear payment intent
    - false: No payment command detected

    ### recipients (string or null)
    - Extract recipient after words: "to", "for", "towards", "at"
    - Clean format: remove special characters, normalize spacing
    - Examples: "Starbucks", "Bob", "coffee shop", "my mom"
    - null: If no clear recipient found

    ### action (string or null)
    - ONLY these values: "pay", "send", "transfer", "give", "wire"
    - Must match exact payment verbs from transcript
    - null: If no payment action detected

    ### amounts (number or null)
    - Convert to CENTS (multiply dollars by 100)
    - Extract numerical values from text: "twenty" → 2000, "$5.50" → 550
    - Use most explicit amount if multiple found
    - null: If no clear amount detected

    ### currency (string)
    - Default: "usd" (always lowercase)
    - Other options: "eur", "gbp", "cad", "jpy", etc.
    - Extract from words like "euros", "pounds", "dollars"

    ## Detection Rules:
    1. Payment keywords: pay, send, transfer, give, wire, donate, tip
    2. Amount indicators: dollars, bucks, $, numbers with currency
    3. Recipient indicators: "to [name]", "for [business]", "at [store]"
    4. Currency indicators: dollars/USD, euros/EUR, pounds/GBP

    ## Example Outputs:

    Input: "Pay 20 dollars to Starbucks"
    Output: {"success": true, "has_payment_command": true, "recipients": "Starbucks", "action": "pay", "amounts": 2000, "currency": "usd"}

    Input: "Send five euros to Bob"  
    Output: {"success": true, "has_payment_command": true, "recipients": "Bob", "action": "send", "amounts": 500, "currency": "eur"}

    Input: "Hello how are you"
    Output: {"success": true, "has_payment_command": false, "recipients": null, "action": null, "amounts": null, "currency": "usd"}

    Input: "Transfer money"
    Output: {"success": true, "has_payment_command": true, "recipients": null, "action": "transfer", "amounts": null, "currency": "usd"}

    ## STRICT REQUIREMENTS:
    - Return ONLY the JSON object
    - No markdown formatting (no ```json```)
    - No additional text before or after JSON
    - All field names must match exactly
    - Boolean values must be true/false (not True/False)
    - Null values must be null (not None or "null")
    - String values must be in quotes
    - Numbers must be integers (amounts in cents)

    RESPOND WITH ONLY THE JSON OBJECT.
    """,
    tools=[analyze_payment_transcript, validate_payment_command]
)