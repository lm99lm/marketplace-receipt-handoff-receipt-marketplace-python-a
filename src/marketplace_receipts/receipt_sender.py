from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Any

from .models import HandoffKind, ReceiptRequest, ReceiptResponse

if TYPE_CHECKING:
    from .infrai_client import InfraiClient


def _money(cents: int, currency: str) -> str:
    return f"{currency} {cents / 100:.2f}"


def build_receipt_email(order: ReceiptRequest) -> dict[str, str]:
    rows = "".join(
        f"<li>{escape(line.title)} x {line.quantity}: "
        f"{_money(line.quantity * line.unit_amount_cents, order.currency)}</li>"
        for line in order.items
    )
    total = sum(line.quantity * line.unit_amount_cents for line in order.items)

    if order.handoff.kind is HandoffKind.DIGITAL:
        if order.handoff.download_url is None:
            raise ValueError("A digital handoff requires download_url")
        handoff = (
            '<p>Your order is ready: '
            f'<a href="{escape(str(order.handoff.download_url))}">download your purchase</a>.</p>'
        )
    else:
        status = order.handoff.status_text or "The seller is preparing your parcel."
        handoff = f"<p>Shipping update: {escape(status)}</p>"

    html = (
        f"<h1>Receipt from {escape(order.seller.shop_name)}</h1>"
        f"<p>Hi {escape(order.buyer.name)}, order {escape(order.order_id)} is confirmed.</p>"
        f"<ul>{rows}</ul><p><strong>Total: {_money(total, order.currency)}</strong></p>"
        f"{handoff}<p>Questions? Email {escape(str(order.seller.support_email))}.</p>"
    )
    return {
        "to": str(order.buyer.email),
        "subject": f"Your {order.seller.shop_name} receipt ({order.order_id})",
        "html": html,
    }


async def send_receipt(order: ReceiptRequest, client: InfraiClient) -> ReceiptResponse:
    data: dict[str, Any] = dict(
        await client.email_send(build_receipt_email(order), f"receipt:{order.order_id}")
    )
    return ReceiptResponse(
        order_id=order.order_id,
        message_id=str(data["message_id"]),
        handoff_kind=order.handoff.kind,
    )
