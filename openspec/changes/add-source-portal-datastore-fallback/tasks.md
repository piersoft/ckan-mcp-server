## 1. Implementation

- [ ] 1.1 Add `extractSourcePortal(resourceUrl, serverUrl)` utility — returns `{ portalUrl, datasetId, resourceId }` or null if same domain
- [ ] 1.2 Add `checkSourceDatastore(sourcePortalUrl, resourceId)` — calls CKAN datastore_info API and returns boolean
- [ ] 1.3 Update `ckan_list_resources` handler: for each resource with `datastore_active` false/null, call `extractSourcePortal` + `checkSourceDatastore`
- [ ] 1.4 Add `check_source_portal` parameter (boolean, default `true`) to the tool schema
- [ ] 1.5 Update markdown and JSON output to include `source_datastore_active` and `source_portal_url` fields when detected
- [ ] 1.6 Add unit tests for `extractSourcePortal` (same domain, different domain, malformed URL)
- [ ] 1.7 Add integration tests for the fallback flow (mock source portal response)
- [ ] 1.8 Update `CLAUDE.md` and `docs/` if needed
