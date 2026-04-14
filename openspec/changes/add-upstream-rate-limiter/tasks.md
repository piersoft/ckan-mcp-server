# Tasks

## 1. Rate limiter module

- [ ] 1.1 Create `src/utils/rate-limiter.ts` with `RateLimitError` class
- [ ] 1.2 Implement `Bucket` type (`tokens`, `lastRefill`)
- [ ] 1.3 Implement `UpstreamRateLimiter` class with `acquire(hostname)` method
- [ ] 1.4 Implement token refill logic (elapsed-based)
- [ ] 1.5 Implement wait-and-retry path up to `maxWaitMs`
- [ ] 1.6 Implement max-size cap (200 hostnames) on bucket map
- [ ] 1.7 Export `getRateLimiter()` singleton factory
- [ ] 1.8 Export `__resetRateLimiterForTests()`
- [ ] 1.9 Export `getRateLimitConfig()` reading env vars

## 2. Integration in `makeCkanRequest`

- [ ] 2.1 Extend `MakeCkanRequestOptions` with `rateLimit?: boolean`
- [ ] 2.2 After cache miss, call `rateLimiter.acquire(resolvedHostname)` when enabled
- [ ] 2.3 Honor `CKAN_RATE_LIMIT_ENABLED=false` and `opts.rateLimit=false` to skip entirely
- [ ] 2.4 Ensure cache hits never reach the rate limiter

## 3. Tests

- [ ] 3.1 Unit: token refill — tokens increase proportional to elapsed time
- [ ] 3.2 Unit: burst — up to `burst` requests fire immediately
- [ ] 3.3 Unit: blocking — request beyond burst waits then proceeds
- [ ] 3.4 Unit: timeout — wait exceeds `maxWaitMs`, throws `RateLimitError`
- [ ] 3.5 Unit: different hostnames get independent buckets
- [ ] 3.6 Unit: `opts.rateLimit=false` bypasses limiter
- [ ] 3.7 Integration: cache hit does not consume a rate limit token

## 4. Docs

- [ ] 4.1 Add env vars to `CLAUDE.md` Known Limitations / configuration section
- [ ] 4.2 Update `openspec/project.md` architecture notes
- [ ] 4.3 Update `LOG.md`

## 5. End-to-end verification

- [ ] 5.1 `npm run build` clean
- [ ] 5.2 `npm test` green
- [ ] 5.3 HTTP server test: 15 rapid identical calls to same portal, verify only first N
      reach upstream (use mocked axios call count to confirm)
- [ ] 5.4 Bump version, commit, tag, release
