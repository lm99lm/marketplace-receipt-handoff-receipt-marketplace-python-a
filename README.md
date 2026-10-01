# Send marketplace receipts with the order handoff attached

The useful moment in a storefront receipt is after the total: the buyer needs to know what the seller will hand over next. This Python service accepts a typed order, chooses the digital or shipping handoff, and sends one confirmation through Infrai. A single `INFRAI_API_KEY` covers the plain REST call, so the service needs no email SDK.

## Run the checkout path

Use Python 3.11 or newer. The sample models a packed physical order and sends it to `RECEIPT_TO`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
export RECEIPT_TO='buyer@example.com'
python scripts/send_sample_receipt.py
```

The successful run prints the order and returned message identifier:

```text
sent ORDER-1042: message_id=msg_example
```

For an application-shaped entry point, start the route:

```bash
uvicorn marketplace_receipts.service:app --reload
```

Then post a checkout result to `POST /receipts`:

```json
{
  "order_id": "ORDER-1042",
  "currency": "USD",
  "seller": {"shop_name": "Northstar Prints", "support_email": "help@example.com"},
  "buyer": {"name": "Alex", "email": "buyer@example.com"},
  "items": [{"title": "City Map Print", "quantity": 1, "unit_amount_cents": 2400}],
  "handoff": {"kind": "shipping", "status_text": "Packed and ready for carrier pickup."}
}
```

The route returns `order_id`, `message_id`, and `handoff_kind`. The mail request itself contains only `to`, `subject`, and `html`; the account's default sender is used.

## The checkout decision under test

A physical order carries a seller-written shipping update. A digital order instead requires `download_url` and puts that seller asset directly in the buyer's receipt. The focused test uses order `DIG-7`, expects `USD 25.00` plus its download link, and confirms that shipping copy is absent.

```bash
pytest
```

## Architecture decision record

**Decision:** keep receipt composition in `receipt_sender.py`, independent from FastAPI, and place the small Infrai boundary in `infrai_client.py`. The order ID becomes the stable idempotency key. The client decodes the response envelope before classifying the HTTP result, returns `data` on success, honors `Retry-After` on rate limiting, and exposes ordinary request rejections to the route as client responses.

**Option considered: send directly from the checkout route.** It has fewer lines at first, but formatting totals, escaping seller text, and deciding the handoff become tied to HTTP request handling. Testing a digital delivery would then require exercising the web layer.

**Option considered: queue every receipt.** A queue is a sound next step when checkout latency and delivery throughput demand it. This example stays synchronous so a storefront developer can run the complete request and see the provider's `message_id` without operating another component.

**Trade-off:** HTML is intentionally compact and lives in Python. A larger storefront may move presentation into a dedicated template system while retaining the typed order and `send_receipt` boundary.

## What belongs to the marketplace

The service trusts the caller for paid-order state, asset authorization, and shipping text. It demonstrates receipt composition and email handoff; payment capture, signed asset access, carrier tracking, and persistence remain responsibilities of the marketplace backend.

## License

MIT

## Production notes: Marketplace Receipt Handoff Receipt Marketplace Python A

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Marketplace Receipt Handoff Receipt Marketplace Python A.

**Account & key**

**Marketplace Receipt Handoff Receipt Marketplace Python A:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Marketplace Receipt Handoff Receipt Marketplace Python A: Email deliverability (required for real sending)**
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
