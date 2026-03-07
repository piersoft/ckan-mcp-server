# data.europa.eu API Reference

European open data portal — API patterns for multi-country and EU-wide queries.

## When to Use

- User asks for EU-wide or multi-country data
- User mentions France (data.gouv.fr is NOT CKAN — use data.europa.eu)
- User wants to compare datasets across countries
- User needs structured/linked data queries via SPARQL

## REST API (Default Path)

Base URL: `https://data.europa.eu/api/hub/search/`

### Search Endpoint

```
GET https://data.europa.eu/api/hub/search/search?q=QUERY&...
```

### Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Full-text query | `q=pollution` |
| `country` | ISO country code(s), comma-separated | `country=IT` or `country=IT,ES` |
| `lang` | Language preference | `lang=it` |
| `page` | Page number (1-based) | `page=1` |
| `limit` | Results per page (max 100) | `limit=10` |
| `sort` | Sort order | `sort=relevance` or `sort=issued+desc` |
| `facets` | Comma-separated facet names | `facets=country,catalog,theme` |
| `theme` | EU data theme URI | `theme=http://publications.europa.eu/resource/authority/data-theme/ENVI` |
| `catalog` | Filter by catalog ID | `catalog=dati-gov-it` |

### Examples

```bash
# Multi-country search (Italy + Spain)
curl "https://data.europa.eu/api/hub/search/search?q=environment&country=IT,ES&limit=10"

# France energy data (since data.gouv.fr is not CKAN)
curl "https://data.europa.eu/api/hub/search/search?q=energie+energy&country=FR&limit=10"

# Filter by EU theme (Environment)
curl "https://data.europa.eu/api/hub/search/search?q=air+quality&theme=http://publications.europa.eu/resource/authority/data-theme/ENVI&limit=10"

# Recent datasets sorted by issue date
curl "https://data.europa.eu/api/hub/search/search?q=climate&sort=issued+desc&limit=10"

# Count datasets by country (facet, no results)
curl "https://data.europa.eu/api/hub/search/search?q=*&facets=country&limit=0"
```

### Response Structure

```json
{
  "success": true,
  "result": {
    "count": 1234,
    "results": [
      {
        "id": "...",
        "title": {"en": "Dataset Title", "it": "Titolo Dataset"},
        "description": {"en": "..."},
        "issued": "2024-01-15",
        "modified": "2024-06-01",
        "country": {"id": "IT", "label": "Italy"},
        "publisher": {"name": "Ministero dell'Ambiente"},
        "themes": ["http://publications.europa.eu/resource/authority/data-theme/ENVI"],
        "distributions": [
          {"url": "https://...", "format": "CSV", "license": "..."}
        ]
      }
    ],
    "facets": {
      "country": [{"id": "IT", "count": 456}, {"id": "ES", "count": 312}],
      "theme": [{"id": "ENVI", "count": 1200}]
    }
  }
}
```

## CKAN-Compatible API

data.europa.eu also exposes a CKAN-compatible endpoint:

```
POST https://data.europa.eu/ckan/api/3/action/package_search
```

Use via MCP tool:

```
ckan_package_search(
  server_url="https://data.europa.eu/ckan",
  q="environment",
  fq="country:IT"
)
```

## SPARQL Endpoint

For structured linked-data queries using RDF/DCAT vocabulary.

```
Endpoint: https://data.europa.eu/sparql
Method: POST
Content-Type: application/x-www-form-urlencoded
Body: query=SELECT...&format=application/sparql-results+json
```

Use via MCP tool: `sparql_query(query="...", endpoint="https://data.europa.eu/sparql")`

### Common Prefixes

```sparql
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
```

### Example Queries

```sparql
-- Datasets about environment from Italy, English titles
SELECT ?dataset ?title ?issued WHERE {
  ?dataset a dcat:Dataset ;
           dct:title ?title ;
           dct:issued ?issued ;
           dct:spatial ?spatial .
  ?spatial skos:exactMatch <http://publications.europa.eu/resource/authority/country/ITA> .
  FILTER(LANG(?title) = "en")
  FILTER(CONTAINS(LCASE(STR(?title)), "environment"))
}
ORDER BY DESC(?issued)
LIMIT 10
```

```sparql
-- Count datasets per country for a topic
SELECT ?country (COUNT(?dataset) AS ?count) WHERE {
  ?dataset a dcat:Dataset ;
           dct:title ?title ;
           dct:spatial ?spatial .
  ?spatial skos:exactMatch ?country .
  FILTER(CONTAINS(LCASE(STR(?title)), "climate"))
}
GROUP BY ?country
ORDER BY DESC(?count)
LIMIT 20
```

## EU Data Themes

| Code | Theme |
|------|-------|
| ENVI | Environment |
| ENER | Energy |
| TRAN | Transport |
| HEAL | Health |
| AGRI | Agriculture, Fisheries, Forestry, Food |
| ECON | Economy and Finance |
| EDUC | Education, Culture, Sport |
| JUST | Justice, Legal System, Public Safety |
| GOVE | Government and Public Sector |
| REGI | Regions and Cities |
| SOCI | Population and Society |
| TECH | Science and Technology |

Full URI pattern: `http://publications.europa.eu/resource/authority/data-theme/{CODE}`

## Country Codes (ISO 3166-1 alpha-2)

| Country | Code | Country | Code |
|---------|------|---------|------|
| Italy | IT | Portugal | PT |
| France | FR | Greece | GR |
| Spain | ES | Netherlands | NL |
| Germany | DE | Belgium | BE |
| Poland | PL | Romania | RO |
| Austria | AT | Sweden | SE |
| Denmark | DK | Finland | FI |
| Ireland | IE | Hungary | HU |
| Croatia | HR | Bulgaria | BG |
