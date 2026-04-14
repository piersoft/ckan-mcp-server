# Tasks

## 1. Cache abstraction

- [ ] 1.1 Create `src/utils/cache.ts` with `CkanCache` interface
- [ ] 1.2 Implement `MemoryLruCache` (Node) with TTL expiry and LRU eviction
- [ ] 1.3 Implement `WorkersCacheApi` wrapper around `caches.default`
- [ ] 1.4 Export `getCache()` factory that picks backend based on runtime detection
- [ ] 1.5 Implement canonical cache-key builder (sorted params → sha1)

## 2. Integration in `makeCkanRequest`

- [ ] 2.1 Add optional `opts?: { cache?: boolean }` parameter
- [ ] 2.2 Compute cache key before HTTP call
- [ ] 2.3 Return cached value on hit (when not bypassed)
- [ ] 2.4 Store result on successful response (success === true, size ≤ ceiling)
- [ ] 2.5 Resolve TTL via action-based policy table with env-var fallback
- [ ] 2.6 Honor `CKAN_CACHE_ENABLED=false` to short-circuit both read and write

## 3. Configuration surface

- [ ] 3.1 Read `CKAN_CACHE_ENABLED`, `CKAN_CACHE_TTL_DEFAULT`, `CKAN_CACHE_MAX_ENTRIES`, `CKAN_CACHE_MAX_ENTRY_BYTES`
- [ ] 3.2 Document env vars in `README.md` and `CLAUDE.md` (remove `No caching` limitation note)
- [ ] 3.3 Expose the same knobs to Workers via `wrangler.toml` `[vars]`

## 4. Tests

- [ ] 4.1 Unit tests for `MemoryLruCache` (set/get/expiry/eviction)
- [ ] 4.2 Unit tests for cache-key canonicalization (param order, missing values)
- [ ] 4.3 Integration test: two identical calls → single upstream hit (use existing mock fixtures)
- [ ] 4.4 Integration test: error response not cached, next call re-hits upstream
- [ ] 4.5 Integration test: `{ cache: false }` bypasses both read and write
- [ ] 4.6 Ensure existing test suite passes with cache enabled (isolate via env var in setup)

## 5. End-to-end verification

- [ ] 5.1 `npm run build` clean
- [ ] 5.2 `npm test` green
- [ ] 5.3 Start HTTP server, call `ckan_package_search` twice with same args, verify second call is faster (log-based or timing-based)
- [ ] 5.4 `npm run dev:worker`, same verification against local Wrangler
- [ ] 5.5 Update `LOG.md` with dated entry

## 6. Docs & release

- [ ] 6.1 Update `project.md` — replace `No caching` with cache description
- [ ] 6.2 Add section to `CLAUDE.md` describing cache config
- [ ] 6.3 Bump version in `package.json` and `manifest.json` (minor)
- [ ] 6.4 Follow release workflow in `CLAUDE.md` (tag, dxt, skill, deploy)
