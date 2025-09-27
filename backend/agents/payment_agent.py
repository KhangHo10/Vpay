#payment_agent.py
from google.adk.agents import BaseAgent
import asyncio

from utils.stripe_service import create_payment_intent

class Payment_Agent(BaseAgent):
    """
    Custom agent that handles Stripe payments.
    Receives a payment intent message and calls stripe_service to confirm payment.
    """    
    # model_config = {"arbitrary_types_allowed": True} # Could be useful
    
    def __init__(self, name="Payment_Agent"):
        super().__init__(name=name)
        
    async def on_message_received(self, message):
        """
        Message format expected:
        {
            "action": "pay",
            "amount": 2000,   # cents
            "currency": "usd",
            "recipient": "Starbucks",
            "payer": "Miguel"
        }
        """
        if message.get("action") != "pay":
            return {"status": "ignored", "reason": "No payment action"}
        
        if message.get("amount") < 0:
            return {"status": "ignored", "reason": "Payment amount is invalid (<0)"}

        amount = message.get("amount")
        currency = message.get("currency", "usd")

        # Call your stripe_service
        result = create_payment_intent(amount, currency)

        # Return result back to workflow or frontend
        return result

payment_doer = BaseAgent(name="Payment_Agent")
def demo_payment():
    message = {
        "action": "pay",
        "amount": 20000,
        "currency": "usd",
        "recipient": "Starbucks",
        "payer": "Miguel"
    }
    
    agent = Payment_Agent()
    run = asyncio.run(agent.on_message_received(message))
    print(run)

if __name__ == "__main__":
    demo_payment()


# Test Stripe connection
# print(test_stripe_connection())
 
# Test creating a payment intent of $20
# intent = create_payment_intent(2000)  # 2000 cents = $20
# print("Payment Intent:", intent)
