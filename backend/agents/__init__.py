#__init__.py

from fastapi import FastAPI, HTTPException
from utils.stripe_service import create_payment_intent

app = FastAPI()

@app.post("/process-payment/")
async def process_payment(amount: int, currency: str, token: str):
    try:
        charge = create_charge(amount, currency, token)
        return {"status": "success", "charge_id": charge.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
