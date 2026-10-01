from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class HandoffKind(StrEnum):
    DIGITAL = "digital"
    SHIPPING = "shipping"


class Seller(BaseModel):
    shop_name: str = Field(min_length=1)
    support_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Buyer(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class OrderLine(BaseModel):
    title: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    unit_amount_cents: int = Field(ge=0)


class Handoff(BaseModel):
    kind: HandoffKind
    download_url: HttpUrl | None = None
    status_text: str | None = None


class ReceiptRequest(BaseModel):
    order_id: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    seller: Seller
    buyer: Buyer
    items: list[OrderLine] = Field(min_length=1)
    handoff: Handoff


class ReceiptResponse(BaseModel):
    order_id: str
    message_id: str
    handoff_kind: HandoffKind
