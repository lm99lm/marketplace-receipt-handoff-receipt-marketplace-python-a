import asyncio
import os

from marketplace_receipts.infrai_client import InfraiClient
from marketplace_receipts.models import ReceiptRequest
from marketplace_receipts.receipt_sender import send_receipt


async def main() -> None:
    api_key = os.environ.get("INFRAI_API_KEY")
    recipient = os.environ.get("RECEIPT_TO")
    if not api_key or not recipient:
        raise SystemExit("Set INFRAI_API_KEY and RECEIPT_TO")

    order = ReceiptRequest.model_validate(
        {
            "order_id": "ORDER-1042",
            "currency": "USD",
            "seller": {"shop_name": "Northstar Prints", "support_email": "help@example.com"},
            "buyer": {"name": "Alex", "email": recipient},
            "items": [{"title": "City Map Print", "quantity": 1, "unit_amount_cents": 2400}],
            "handoff": {"kind": "shipping", "status_text": "Packed and ready for carrier pickup."},
        }
    )
    client = InfraiClient(api_key)
    try:
        result = await send_receipt(order, client)
        print(f"sent {result.order_id}: message_id={result.message_id}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
