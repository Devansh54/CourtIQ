# CourtIQ — Sportradar Tennis API Integration & Specifications

**Product Name:** CourtIQ – Tennis Data & Analytics Explorer  
**API Provider:** Sportradar Tennis API (v3 Trial)  
**API Documentation:** [Sportradar Developer Portal](https://developer.sportradar.com/tennis/reference/tennis-overview)  
**Lead Architect:** Devansh  

---

## 1. API Architecture & Authentication Overview

CourtIQ integrates with the Sportradar Tennis API (v3) to harvest tennis competition hierarchies, venue infrastructures, and player doubles rankings. The Sportradar API delivers data in nested JSON format over HTTPS.

### 1.1 Authentication
Authentication is conducted using an API key issued by Sportradar. The key must be transmitted either as a query parameter or as an HTTP header:
- **Query Parameter:** `?api_key={SPORTRADAR_API_KEY}`
- **HTTP Header:** `x-api-key: {SPORTRADAR_API_KEY}`

The key is managed strictly through `.env` and loaded by `src/courtiq/core/config.py`. It is never hardcoded or committed to version control.

### 1.2 Rate Limiting & Quotas (Trial Tier)
The Sportradar Tennis Trial tier enforces stringent rate limits:
- **Rate Limit:** 1 request per second (1.0 RPS).
- **Monthly Quota:** 1,000 requests per month.
- **HTTP Error on Breach:** `429 Too Many Requests`.

CourtIQ's `SportradarClient` (`src/courtiq/core/api_client.py`) implements a rate-limiting controller that paces outgoing requests (minimum 1.0 second delay between calls) and applies exponential backoff when a `429` status code is encountered.

---

## 2. API Endpoints Specification

### 2.1 Competitions Endpoint (Devansh's Domain)
- **Official Reference:** [Sportradar Competitions Reference](https://developer.sportradar.com/tennis/reference/competitions)
- **HTTP Method:** `GET`
- **Trial Base URL:** `https://api.sportradar.com/tennis/trial/v3/en/competitions.json`
- **Output Tables:** `categories`, `competitions`

#### Sample JSON Response Structure:
```json
{
  "generated_at": "2024-11-04T12:00:00Z",
  "competitions": [
    {
      "id": "sr:competition:101",
      "name": "ATP Australian Open",
      "parent_id": null,
      "type": "singles",
      "gender": "men",
      "category": {
        "id": "sr:category:1",
        "name": "ATP"
      }
    },
    {
      "id": "sr:competition:102",
      "name": "ATP Australian Open Doubles",
      "parent_id": "sr:competition:101",
      "type": "doubles",
      "gender": "men",
      "category": {
        "id": "sr:category:1",
        "name": "ATP"
      }
    }
  ]
}
```

#### Field Mapping:
| JSON Path | Relational Target | Constraints / Transformation |
|---|---|---|
| `competitions[].category.id` | `categories.category_id` | Primary Key, Deduplicated |
| `competitions[].category.name` | `categories.category_name` | NOT NULL |
| `competitions[].id` | `competitions.competition_id` | Primary Key |
| `competitions[].name` | `competitions.competition_name` | NOT NULL |
| `competitions[].parent_id` | `competitions.parent_id` | Nullable, Foreign Key |
| `competitions[].type` | `competitions.type` | NOT NULL |
| `competitions[].gender` | `competitions.gender` | NOT NULL |
| `competitions[].category.id` | `competitions.category_id` | Foreign Key REFERENCES categories(category_id) |

---

### 2.2 Complexes Endpoint (Venue & Complexes Owner's Domain)
- **Official Reference:** [Sportradar Complexes Reference](https://developer.sportradar.com/tennis/reference/complexes)
- **HTTP Method:** `GET`
- **Trial Base URL:** `https://api.sportradar.com/tennis/trial/v3/en/complexes.json`
- **Output Tables:** `complexes`, `venues`

#### Sample JSON Response Structure:
```json
{
  "generated_at": "2024-11-04T12:00:00Z",
  "complexes": [
    {
      "id": "sr:complex:12",
      "name": "Melbourne Park",
      "venues": [
        {
          "id": "sr:venue:34",
          "name": "Rod Laver Arena",
          "city_name": "Melbourne",
          "country_name": "Australia",
          "country_code": "AUS",
          "timezone": "Australia/Melbourne"
        },
        {
          "id": "sr:venue:35",
          "name": "Margaret Court Arena",
          "city_name": "Melbourne",
          "country_name": "Australia",
          "country_code": "AUS",
          "timezone": "Australia/Melbourne"
        }
      ]
    }
  ]
}
```

#### Field Mapping:
| JSON Path | Relational Target | Constraints / Transformation |
|---|---|---|
| `complexes[].id` | `complexes.complex_id` | Primary Key |
| `complexes[].name` | `complexes.complex_name` | NOT NULL |
| `complexes[].venues[].id` | `venues.venue_id` | Primary Key |
| `complexes[].venues[].name` | `venues.venue_name` | NOT NULL |
| `complexes[].venues[].city_name` | `venues.city_name` | NOT NULL |
| `complexes[].venues[].country_name` | `venues.country_name` | NOT NULL |
| `complexes[].venues[].country_code` | `venues.country_code` | CHAR(3) NOT NULL |
| `complexes[].venues[].timezone` | `venues.timezone` | NOT NULL |
| `complexes[].id` | `venues.complex_id` | Foreign Key REFERENCES complexes(complex_id) |

---

### 2.3 Doubles Competitor Rankings Endpoint (Rankings Owner's Domain)
- **Official Reference:** [Sportradar Doubles Competitor Rankings Reference](https://developer.sportradar.com/tennis/reference/doubles-competitor-rankings)
- **HTTP Method:** `GET`
- **Trial Base URL:** `https://api.sportradar.com/tennis/trial/v3/en/double_competitor_rankings.json`
- **Output Tables:** `competitors`, `competitor_rankings`

#### Sample JSON Response Structure:
```json
{
  "generated_at": "2024-11-04T12:00:00Z",
  "rankings": [
    {
      "name": "ATP Doubles",
      "year": 2024,
      "week": 44,
      "competitor_rankings": [
        {
          "rank": 1,
          "movement": 0,
          "points": 7820,
          "competitions_played": 22,
          "competitor": {
            "id": "sr:competitor:101",
            "name": "Granollers, Marcel",
            "country": "Spain",
            "country_code": "ESP",
            "abbreviation": "GRA"
          }
        }
      ]
    }
  ]
}
```

#### Field Mapping:
| JSON Path | Relational Target | Constraints / Transformation |
|---|---|---|
| `competitor.id` | `competitors.competitor_id` | Primary Key |
| `competitor.name` | `competitors.name` | NOT NULL |
| `competitor.country` | `competitors.country` | NOT NULL |
| `competitor.country_code` | `competitors.country_code` | CHAR(3) NOT NULL |
| `competitor.abbreviation` | `competitors.abbreviation` | VARCHAR(10) NOT NULL |
| `rank` | `competitor_rankings.rank` | INT NOT NULL |
| `movement` | `competitor_rankings.movement` | INT NOT NULL |
| `points` | `competitor_rankings.points` | INT NOT NULL |
| `competitions_played` | `competitor_rankings.competitions_played` | INT NOT NULL |
| `competitor.id` | `competitor_rankings.competitor_id` | Foreign Key REFERENCES competitors(competitor_id) |

---

## 3. Synthetic Mock Fixtures & Offline Architecture

To guarantee that the application can be developed, tested, and demonstrated without requiring active, paid, or network-bound Sportradar credentials:
1. Synthetic JSON fixtures reflecting actual Sportradar structures are located in:
   - `tests/fixtures/competitions_sample.json`
   - `tests/fixtures/complexes_sample.json`
   - `tests/fixtures/rankings_sample.json`
2. `SportradarClient` automatically operates in offline mock mode if:
   - `SPORTRADAR_API_KEY` is empty, unset, or set to placeholder values.
   - Network requests fail due to unreachable host or expired API trial credentials.
3. In mock mode, the client logs an informational notice and yields verified fixture data, enabling full ETL execution, database population, and Streamlit testing.
