from marketplace_receipts.models import ReceiptRequest
from marketplace_receipts.receipt_sender import build_receipt_email


def test_digital_order_places_seller_asset_in_buyer_receipt() -> None:
    order = ReceiptRequest.model_validate(
        {
            "order_id": "DIG-7",
            "currency": "USD",
            "seller": {"shop_name": "Pixel Market", "support_email": "seller@example.com"},
            "buyer": {"name": "Mina", "email": "buyer@example.com"},
            "items": [{"title": "Checkout Icons", "quantity": 2, "unit_amount_cents": 1250}],
            "handoff": {"kind": "digital", "download_url": "https://assets.example.com/orders/DIG-7"},
        }
    )

    email = build_receipt_email(order)

    assert email["to"] == "buyer@example.com"
    assert "USD 25.00" in email["html"]
    assert "https://assets.example.com/orders/DIG-7" in email["html"]
    assert "Shipping update" not in email["html"]
