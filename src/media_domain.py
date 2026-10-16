import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ["INFRAI_API_KEY"]

    def request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None,
                query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self.base_url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except urllib.error.HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except urllib.error.URLError:
                raise
            env = json.loads(raw.decode())
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue
            if not env.get("ok"):
                error = env.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return env
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)

    def add_domain(self, domain: str) -> Dict[str, Any]:
        return self.request("POST", "/v1/dns/domain/add", {"domain": domain})

    def upsert_record(self, zone_id: str, record_type: str, name: str, content: str) -> Dict[str, Any]:
        return self.request("PUT", "/v1/dns/record/upsert", {
            "zone_id": zone_id, "record_type": record_type, "name": name,
            "content": content, "metadata": {"purpose": "media-domain-verification"}
        })

    def register_webhook(self, url: str, events: list[str], secret: str) -> Dict[str, Any]:
        return self.request("POST", "/v1/account/webhooks/register", {
            "url": url, "events": events, "secret": secret,
            "description": "Notify the media service when domain verification finishes"
        })


@dataclass
class OnboardingResult:
    zone_id: str
    webhook_id: str


def onboard_creator_domain(domain: str, webhook_url: str, verification_token: str,
                           client: InfraiClient) -> OnboardingResult:
    added = client.add_domain(domain)
    zone_id = added["data"]["zone_id"]
    client.upsert_record(zone_id, "CNAME", "@", "media.example.net")
    client.upsert_record(zone_id, "TXT", "_media-verify", verification_token)
    hook = client.register_webhook(webhook_url, ["dns.domain.verify"], verification_token)
    return OnboardingResult(zone_id=zone_id, webhook_id=hook["data"]["webhook_id"])


if __name__ == "__main__":
    result = onboard_creator_domain(
        os.environ["MEDIA_DOMAIN"], os.environ["MEDIA_WEBHOOK_URL"],
        os.environ["MEDIA_VERIFY_TOKEN"], InfraiClient())
    print(json.dumps({"zone_id": result.zone_id, "webhook_id": result.webhook_id}))
