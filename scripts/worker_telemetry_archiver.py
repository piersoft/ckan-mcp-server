"""
Cloudflare Worker Telemetry Archiver
Scarica eventi di telemetria del Worker e aggiorna worker_events_flat.jsonl.
Non persiste il file raw: fetch → flatten → dedup → append, tutto in memoria.
Legge CF_API_TOKEN da env var (GHA) o da .env nella root del progetto.
"""

import json
import os
import time
from pathlib import Path

import requests

# Carica .env dalla root del progetto (fallback rispetto a env var di sistema)
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            if k not in os.environ:  # env var di sistema ha priorità
                os.environ[k] = v.strip().strip('"')

ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "c89b6bdafbbb793bf64cfa3b271fa5a4")
API_TOKEN = os.environ.get("CF_API_TOKEN", "")
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FLAT_FILE = DATA_DIR / "worker_events_flat.jsonl"
STATE_FILE = DATA_DIR / "worker_telemetry_last_run.json"
DAY_MS = 86400 * 1000


def get_last_run_ms(backfill_days=1):
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())["last_run_ms"]
    return int(time.time() * 1000) - backfill_days * DAY_MS


def save_last_run_ms(ms):
    STATE_FILE.write_text(json.dumps({"last_run_ms": ms}))


def fetch_events(from_ms, to_ms):
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}"
        "/workers/observability/telemetry/query"
    )
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    all_events, offset = [], None

    while True:
        # queryId univoco per ogni run: evita che l'API riusi la query salvata
        body = {
            "queryId": f"archiver-{to_ms}",
            "timeframe": {"from": from_ms, "to": to_ms},
            "view": "events",
            "limit": 2000,
            "parameters": {
                "filters": [
                    {
                        "key": "$metadata.type",
                        "operation": "eq",
                        "type": "string",
                        "value": "cf-worker",
                    }
                ],
                "filterCombination": "and",
                "orderBy": {"value": "timestamp", "order": "asc"},
            },
        }
        if offset:
            body["offset"] = offset

        resp = requests.post(url, headers=headers, json=body)
        if not resp.ok:
            print(f"  ERRORE {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        data = resp.json()
        events = data.get("result", {}).get("events", {}).get("events", [])
        all_events.extend(events)
        print(f"  Scaricati {len(events)} eventi (totale: {len(all_events)})")

        next_offset = data.get("result", {}).get("events", {}).get("nextOffset")
        if not next_offset or len(events) == 0:
            break
        offset = next_offset

    return all_events


def extract_query(source: dict) -> str | None:
    if source.get("tool") == "ckan_find_portals":
        parts = []
        for key in ("country", "query", "language", "has_datastore", "min_datasets"):
            val = source.get(key)
            if val is not None:
                parts.append(f"{key}={val}")
        return " ".join(parts) or None

    return (
        source.get("q")
        or source.get("query")
        or source.get("id")
        or source.get("pattern")
        or source.get("sql")
        or source.get("resource_id")
    )


def flatten(event: dict) -> dict | None:
    workers = event.get("$workers", {})
    metadata = event.get("$metadata", {})
    source = event.get("source", {})

    # Escludi GET probe (senza tool)
    method = workers.get("event", {}).get("request", {}).get("method")
    if method == "GET":
        return None

    ts_ms = event.get("timestamp", 0)
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts_ms / 1000))

    return {
        "id": metadata.get("id"),
        "timestamp": ts_iso,
        "outcome": workers.get("outcome"),
        "tool": source.get("tool") if isinstance(source, dict) else None,
        "server": source.get("server") if isinstance(source, dict) else None,
        "query": extract_query(source) if isinstance(source, dict) else None,
        "error": metadata.get("error"),
    }


def load_existing_flat() -> dict[str, dict]:
    """Carica flat file esistente. Ritorna dict id→record."""
    existing: dict[str, dict] = {}
    if FLAT_FILE.exists():
        for line in FLAT_FILE.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("id"):
                    existing[rec["id"]] = rec
    return existing


def update_flat(new_events: list) -> tuple[int, int]:
    """Flattena nuovi eventi, dedup contro flat esistente, riscrive il file."""
    existing = load_existing_flat()
    added = 0
    skipped_get = 0

    for event in new_events:
        flat = flatten(event)
        if flat is None:
            skipped_get += 1
            continue
        eid = flat.get("id")
        if eid and eid not in existing:
            existing[eid] = flat
            added += 1

    # Riscrivi ordinato per timestamp asc
    records = sorted(existing.values(), key=lambda r: r.get("timestamp", ""))
    with open(FLAT_FILE, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    return added, skipped_get


def run(once=True, backfill_days=1):
    """
    once=True        → esegui una volta sola
    once=False       → loop ogni 24 ore (modalità daemon)
    backfill_days    → giorni da recuperare alla prima esecuzione (default 1, max 7)
                       usa chunk da 24h per evitare downsampling API
    """
    while True:
        now_ms = int(time.time() * 1000)
        from_ms = get_last_run_ms(backfill_days)

        # Suddividi in chunk da 24h per evitare downsampling
        chunks = []
        cursor = from_ms
        while cursor < now_ms:
            chunk_end = min(cursor + DAY_MS, now_ms)
            chunks.append((cursor, chunk_end))
            cursor = chunk_end

        all_events = []
        for chunk_from, chunk_to in chunks:
            from_dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(chunk_from / 1000))
            to_dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(chunk_to / 1000))
            print(f"Chunk: {from_dt} → {to_dt}")
            events = fetch_events(chunk_from, chunk_to)
            all_events.extend(events)

        if all_events:
            added, skipped_get = update_flat(all_events)
            total = sum(1 for _ in FLAT_FILE.read_text().splitlines() if _.strip())
            print(f"  Scaricati: {len(all_events)} | Nuovi nel flat: {added} | GET esclusi: {skipped_get} | Totale flat: {total}")
        else:
            print("  Nessun evento nuovo.")

        save_last_run_ms(now_ms)

        if once:
            break
        print("Aspetto 24 ore...\n")
        time.sleep(DAY_MS // 1000)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cloudflare Worker Telemetry Archiver")
    parser.add_argument("--daemon", action="store_true", help="Loop ogni 24 ore")
    parser.add_argument(
        "--backfill-days",
        type=int,
        default=1,
        help="Giorni da recuperare alla prima esecuzione (default: 1, max: 7)",
    )
    args = parser.parse_args()

    run(once=not args.daemon, backfill_days=args.backfill_days)
