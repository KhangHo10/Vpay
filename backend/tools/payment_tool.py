# payment_tool.py
import asyncio
from google.adk.agents import BaseAgent
from utils.stripe_service import create_payment_intent

class Payment_Tool(BaseAgent):
    """
    ADK-compatible agent that handles Stripe payments.
    Receives a payment intent message and calls stripe_service to create/confirm payment.
    """

    def __init__(self, name="Payment_Tool"):
        super().__init__(name=name)

    async def on_message_received(self, message):
        """
        Expected message format:
        {
            "action": "pay",
            "amount": 2000,   # cents
            "currency": "usd",
            "recipient": "Starbucks",
            "payer": "Miguel"
        }
        """
        # Basic validation
        if message.get("action") != "pay":
            return {"status": "ignored", "reason": "No payment action"}

        amount = message.get("amount")
        if amount is None or amount < 0:
            return {"status": "ignored", "reason": "Payment amount invalid"}

        currency = message.get("currency", "usd")

        # Call Stripe service
        try:
            result = create_payment_intent(amount, currency)
        except Exception as e:
            return {"status": "error", "reason": str(e)}

        # Return result back to ADK workflow
        return result


# Demo/testing
async def demo_payment():
    test_message = {
        "action": "pay",
        "amount": 20000,  # $200
        "currency": "usd",
        "recipient": "Starbucks",
        "payer": "Miguel"
    }

    agent = Payment_Tool()
    result = await agent.on_message_received(test_message)
    print("Demo Payment Result:", result)


if __name__ == "__main__":
    asyncio.run(demo_payment())
