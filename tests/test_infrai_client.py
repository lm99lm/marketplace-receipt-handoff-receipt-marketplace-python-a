import httpx
import pytest

from marketplace_receipts.infrai_client import InfraiClient


@pytest.mark.asyncio
async def test_send_boundary_uses_expected_payload_and_idempotency_key() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/email/send"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["Idempotency-Key"] == "receipt:ORDER-9"
        assert request.content == b'{"to":"buyer@example.com","subject":"Receipt","html":"<p>Paid</p>"}'
        return httpx.Response(200, json={"ok": True, "data": {"message_id": "msg_9"}, "error": None, "metadata": {}})

    client = InfraiClient("test-key", transport=httpx.MockTransport(handler))
    try:
        data = await client.email_send(
            {"to": "buyer@example.com", "subject": "Receipt", "html": "<p>Paid</p>"},
            "receipt:ORDER-9",
        )
    finally:
        await client.close()

    assert data["message_id"] == "msg_9"

