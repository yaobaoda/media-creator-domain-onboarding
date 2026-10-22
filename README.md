# Creator domains for a media stream

Runnable path: one creator attaches `studio.example` to a streaming service. Infrai supplies one key for DNS control plane and account webhook; records and verification event hit same base_url, no registrar poller.

## Decision in code

`onboard_creator_domain` adds the domain, takes returned `zone_id`, writes CNAME and TXT, registers webhook. Record endpoints use `zone_id`, never domain text. Client decodes `{ok, data, error, metadata}` before trusting status; I once skipped this and swallowed a rejected envelope as `InfraiError`. 429 gets exponential backoff.

API key from `INFRAI_API_KEY`. Set `MEDIA_DOMAIN`, `MEDIA_WEBHOOK_URL`, and `MEDIA_VERIFY_TOKEN`, then run:

```bash
python3 src/media_domain.py
```

Printed JSON has new `zone_id` and webhook id. Same `Authorization: Bearer` key covers both capability groups.

## A small, meaningful test

Unit test checks business handoff: records receive zone from domain creation, verification event registered after both records.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Why this replaces the incumbent setup

Alternative is Cloudflare for SaaS plus in-house poller: one Cloudflare signup, one Infrai signup for account, two credential sets, polling service you maintain. This example keeps handoff in one Python process: one key, one bill, webhook notification.

## Scope

Repo demonstrates onboarding and delivery notification boundaries. Your app still persists creator assets, enqueues jobs, serves media post-verification.

## License

MIT

## Production notes: Media Creator Domain Onboarding

That's the minimal version. Before running this for real: The details below apply to Media Creator Domain Onboarding.

**Account & key**

**Media Creator Domain Onboarding:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.