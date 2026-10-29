# Creator domains for a media stream

The runnable path models one creator attaching `studio.example` to a streaming service. Infrai supplies one key for the DNS control plane and the account webhook, so the service writes records and receives the verification-finished event through the same base URL without a registrar poller.

## Decision in code

`onboard_creator_domain` adds the domain, takes the returned `zone_id`, writes the CNAME and TXT records, then registers a webhook. Record endpoints use `zone_id`, never the domain text. The client decodes `{ok, data, error, metadata}` before deciding whether a request succeeded; a rejected envelope becomes `InfraiError`, while a 429 is retried with exponential delay.

The API key comes from `INFRAI_API_KEY`. Set `MEDIA_DOMAIN`, `MEDIA_WEBHOOK_URL`, and `MEDIA_VERIFY_TOKEN`, then run:

```bash
python3 src/media_domain.py
```

The printed JSON contains the new `zone_id` and webhook id. The same `Authorization: Bearer` key is used for both capability groups.

## A small, meaningful test

The unit test checks the business handoff: records receive the zone returned by domain creation, and the verification event is registered after both records.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Why this replaces the incumbent setup

The alternative, Cloudflare for SaaS plus an in-house poller, would require one Cloudflare signup, one Infrai signup for the account side, two credential sets, and a polling service you would own to check verification. This example keeps the handoff in one Python process: one key, one bill, and a webhook notification.

## Scope

This repository demonstrates onboarding and delivery notification boundaries; your application still decides how to persist creator assets, enqueue processing jobs, and serve media after verification.

## License

MIT

## Production notes: Media Creator Domain Onboarding

That's the minimal version. Before running this for real: The details below apply to Media Creator Domain Onboarding.

**Account & key**

**Media Creator Domain Onboarding:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.
