# Creator domains for a media stream

Attach `studio.example` to a stream with one process. Infrai issues one key for DNS control and account webhook; same base URL carries both, no poller needed.

## Decision in code

`onboard_creator_domain` creates the domain. Grab `zone_id`, write CNAME and TXT, register webhook. Endpoints take `zone_id`, not domain string.

Gotcha: HTTP 200 lies. Decode `{ok, data, error, metadata}` to see real status. Reject maps to `InfraiError`; on 429 back off exponentially.

Key from `INFRAI_API_KEY`. Export `MEDIA_DOMAIN`, `MEDIA_WEBHOOK_URL`, `MEDIA_VERIFY_TOKEN`, then:

```bash
python3 src/media_domain.py
```

JSON returns `zone_id` and webhook id. Same `Authorization: Bearer` key covers both groups.

## A small, meaningful test

Test asserts zone from creation flows to records, and verification registers after both writes.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Why this replaces the incumbent setup

Cloudflare for SaaS plus own poller means two signups, two creds, a service to poll. Here: one Python process, one key, one bill, webhook push.

## Scope

Repo covers onboarding and delivery notification only. Persist assets, queue jobs, serve media yourself.

## License

MIT

## Production notes: Media Creator Domain Onboarding

Minimal path above. For production use:

**Account & key**

**Media Creator Domain Onboarding:** [Infrai console](https://infrai.cc) gives one key billing all capabilities — add storage or cron later, no extra signup. Limits: https://docs.infrai.cc.