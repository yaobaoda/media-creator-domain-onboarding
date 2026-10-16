from media_domain import OnboardingResult, onboard_creator_domain


class FakeClient:
    def __init__(self):
        self.calls = []

    def add_domain(self, domain):
        self.calls.append(("add", domain))
        return {"data": {"zone_id": "zone-123"}}

    def upsert_record(self, zone_id, record_type, name, content):
        self.calls.append(("record", zone_id, record_type, name, content))
        return {"data": {}}

    def register_webhook(self, url, events, secret):
        self.calls.append(("webhook", url, events, secret))
        return {"data": {"webhook_id": "hook-9"}}


def test_records_use_zone_id_before_webhook():
    client = FakeClient()
    result = onboard_creator_domain("studio.example", "https://studio.test/events", "token", client)
    assert result == OnboardingResult("zone-123", "hook-9")
    assert client.calls[1][1] == "zone-123"
    assert client.calls[2][2] == "TXT"
    assert client.calls[3][2] == ["dns.domain.verify"]
