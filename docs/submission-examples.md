# Submission Examples

Three working examples for the Anthropic Connectors Directory submission form.
Each example shows a natural language prompt, which tool Claude invokes, and the actual output.

---

## Example 1 — Journalist searching for open data on a topic

**Persona**: Journalist or citizen wanting to find relevant datasets without knowing the portal structure.

**User prompt**:
> What open data about air quality is available on Italy's national open data portal?

**Tool invoked**: `ckan_find_relevant_datasets`

**Arguments**:
```json
{
  "server_url": "https://www.dati.gov.it/opendata",
  "query": "air quality pollution monitoring",
  "limit": 5
}
```

**Output** (excerpt):

```
# Relevant CKAN Datasets

Server: https://www.dati.gov.it/opendata
Query: air quality pollution monitoring

| Rank | Dataset                                    | Score | Title                                            | Org             | Tags                              |
|------|--------------------------------------------|-------|--------------------------------------------------|-----------------|-----------------------------------|
|    1 | impianti-industriali-soggetti-ad-aia       |     3 | Impianti industriali soggetti ad AIA             | GeoDati - RNDT  | air, air-pollution, air-quality   |
|    2 | qualita-dellaria-campioni-inquinanti-dataset |  3 | Qualità dell'Aria Campioni inquinanti - Dataset  | GeoDati - RNDT  | air-quality, aqd                  |
```

**Why it's useful**: No CKAN knowledge required. Claude translates a natural language topic into a ranked search across titles, descriptions, tags, and organizations.

---

## Example 2 — Policy analyst exploring a national portal

**Persona**: Public servant, researcher, or journalist wanting a quick overview of what a portal contains.

**User prompt**:
> Give me an overview of Italy's national open data portal — how many datasets, main categories, most common formats, most active organizations.

**Tool invoked**: `ckan_catalog_stats`

**Arguments**:
```json
{
  "server_url": "https://www.dati.gov.it/opendata"
}
```

**Output** (excerpt):

```
# CKAN Portal Statistics

Server: https://www.dati.gov.it/opendata
Total datasets: 69,476

## Categories
- governo:    35,502
- societa:     9,072
- ambiente:    8,971
- economia:    6,778
- regioni:     4,929

## Formats
- CSV:   44,208
- JSON:  14,973
- ZIP:   11,578
- XML:   11,563

## Top Organizations
- regione-toscana:          12,735
- geodati-gov-it-rndt:       8,686
- regione-veneto:            6,568
```

**Why it's useful**: A single prompt gives a complete, structured overview of a portal — useful for deciding where to invest research time or assessing a portal's openness.

---

## Example 3 — Data analyst querying tabular data directly

**Persona**: Data analyst or developer who wants to inspect actual records from a dataset without downloading files.

**User prompt**:
> Show me the latest municipal ordinances published by the City of Messina.

**Tool invoked**: `ckan_datastore_search`

**Arguments**:
```json
{
  "server_url": "https://dati.comune.messina.it",
  "resource_id": "17301b8b-2a5b-425f-80b0-5b75bb1793e9",
  "limit": 5
}
```

**Output** (excerpt):

```
# DataStore Query Results

Server: https://dati.comune.messina.it
Total Records: 2,066 | Returned: 5

## Fields
- numero (numeric), data_pubblicazione (timestamp), inizio_validita (text),
  fine_validita (text), aree (text), tipo (text), sintesi (text)

## Records

| numero | data_pubblicazione  | aree                          | tipo                          | sintesi                  |
|--------|---------------------|-------------------------------|-------------------------------|--------------------------|
|    382 | 2026-03-06          | Via Garibaldi; Viale Boccetta | lavori; divieto_sosta         | Richiesta ordinanza ...  |
|    381 | 2026-03-06          | Via Maddalena; Viale S.Martino| lavori; divieto_sosta         | Occupazione temporane... |
|    380 | 2026-03-06          | Viale Europa; Via G. Pilli    | lavori; divieto_transito      | Reti Infrastruttura D... |

More results available: use offset: 5 for next page.
```

**Why it's useful**: Claude can query tabular data from any CKAN DataStore resource with SQL-like filtering, pagination, and field selection — turning a portal into a live database accessible through natural language.

---

## Summary

| Example | Portal | Tool | Persona |
|---------|--------|------|---------|
| 1 — Find datasets by topic | dati.gov.it (IT) | `ckan_find_relevant_datasets` | Journalist / citizen |
| 2 — Portal overview | dati.gov.it (IT) | `ckan_catalog_stats` | Policy analyst / researcher |
| 3 — Query tabular data | dati.comune.messina.it (IT) | `ckan_datastore_search` | Data analyst / developer |

All examples tested against live CKAN portals on 2026-03-07.
