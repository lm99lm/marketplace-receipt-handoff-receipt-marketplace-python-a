import os

from fastapi import FastAPI, HTTPException

from .infrai_client import InfraiClient, InfraiError
from .models import ReceiptRequest, ReceiptResponse
from .receipt_sender import send_receipt

app = FastAPI(title="Marketplace receipt handoff")


@app.post("/receipts", response_model=ReceiptResponse)
async def create_receipt(order: ReceiptRequest) -> ReceiptResponse:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="INFRAI_API_KEY is not configured")

    client = InfraiClient(api_key)
    try:
        return await send_receipt(order, client)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InfraiError as exc:
        caller_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=caller_status,
            detail={"code": exc.code, "error": exc.detail},
        ) from exc
    finally:
        await client.close()

