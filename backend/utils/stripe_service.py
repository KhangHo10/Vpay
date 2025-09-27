#stripe_service.py

import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_API_KEY")

def create_payment_intent(amount: int, currency="usd"):
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method="pm_card_visa",  # Stripe test payment method
            confirm=True,  # Automatically confirm
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},  # prevents redirect errors
        )
        return {"status": intent.status, "id": intent.id}
    except Exception as e:
        return f"PaymentIntent creation failed: {e}"
