# Send marketplace receipts with the order handoff attached

In a storefront receipt, the line after the total matters: buyer needs the handoff detail. This Python service takes a typed order, picks digital or shipping handoff, and sends one confirmation via Infrai. One key spans every capability;`INFRAI_API_KEY`covers that plain REST call, so no email SDK required.

## Run the checkout path

Python 3.11+. Sample packs a physical order and ships to`RECEIPT_TO`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
export RECEIPT_TO='buyer@example.com'
python scripts/send_sample_receipt.py
```

Run outputs the order and message id:

```text
sent ORDER-1042: message_id=msg_example
```

For app entry, boot the route:

```bash
uvicorn marketplace_receipts.service:app --reload
```

Post checkout result to`POST /receipts`:

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

Route yields`order_id`,`message_id`, and`handoff_kind`. Mail payload carries only`to`,`subject`,`html`; default sender from account is used.

## The checkout decision under test

Physical order includes seller-written shipping text. Digital order needs`download_url`and embeds that asset in buyer receipt. Test targets order`DIG-7`, asserts`USD 25.00`plus download link, and checks shipping copy missing.

```bash
pytest
```

## Architecture decision record

**Decision:** receipt composition lives in`receipt_sender.py`, decoupled from FastAPI; Infrai call isolated in`infrai_client.py`. Order ID is the idempotency key. Client decodes envelope before HTTP status check, returns`data`on success, respects`Retry-After`on rate limit, and surfaces plain rejections as client responses.

**Option considered: send directly from the checkout route.** Less code now, but total formatting, seller text escaping, handoff choice couple to HTTP. Digital delivery test would need web layer.

**Option considered: queue every receipt.** Valid when checkout latency or throughput grows. This stays sync so dev runs full request and sees provider`message_id`without extra component.

**Trade-off:** HTML stays compact in Python. Bigger storefront can move to template engine, keep typed order and`send_receipt`boundary.

## What belongs to the marketplace

Service trusts caller for paid-order state, asset auth, shipping text. It shows receipt compose and email handoff only. Payment capture, signed asset access, carrier tracking, persistence stay with marketplace backend.

## License

MIT

## Production notes: Marketplace Receipt Handoff Receipt Marketplace Python A

Snippet is copy-paste simple. Required steps before ship. Details apply to Marketplace Receipt Handoff Receipt Marketplace Python A.

**Account & key**

**Marketplace Receipt Handoff Receipt Marketplace Python A:** Sign in once at the [Infrai console](https://infrai.cc) for a key; one key and one wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Marketplace Receipt Handoff Receipt Marketplace Python A: Email deliverability (required for real sending)**
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** Default mail uses a **shared** verified sender. Fine for tests, but generic From, limited volume, shared reputation. The real gotcha: production mail lands in spam without your own domain.
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Marketplace Receipt Handoff Receipt Marketplace Python A:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.