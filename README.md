# DevTrack

## EventHub assignment

The separate EventHub Django REST Framework project is in [`eventhub/`](eventhub/README.md). Follow its README to install dependencies, migrate its SQLite database, run the API, and import its Postman collection.

DevTrack is a small Django API for reporters to file engineering issues, assign priorities, and track status. It stores records in JSON files to keep the project easy to run without a database.

## Run locally

From the project root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000`.

## Endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| `POST` | `/api/reporters/` | Create a reporter |
| `GET` | `/api/reporters/` | List reporters |
| `GET` | `/api/reporters/?id=1` | Get one reporter; returns 404 when missing |
| `POST` | `/api/issues/` | Create an issue and return its priority-specific message |
| `GET` | `/api/issues/` | List issues |
| `GET` | `/api/issues/?id=1` | Get one issue; returns 404 when missing |
| `GET` | `/api/issues/?status=open` | Filter issues by status |

POST requests use `Content-Type: application/json`. A reporter must exist before an issue can refer to its `reporter_id`.

### Create a reporter

```json
{
  "id": 1,
  "name": "Alice Example",
  "email": "alice@example.com",
  "team": "backend"
}
```

### Create an issue

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

Allowed statuses are `open`, `in_progress`, `resolved`, and `closed`. Allowed priorities are `low`, `medium`, `high`, and `critical`.

## Validation and storage behavior

- IDs may be supplied by the client or generated automatically. Duplicate IDs return `409 Conflict`.
- Invalid JSON, empty names or titles, invalid emails, and unsupported status or priority values return `400 Bad Request`.
- Creating an issue with an unknown reporter returns `404 Not Found`.
- JSON files are replaced atomically after writes. Invalid or unreadable data files return `500` instead of being treated as empty.
- `issues.json` stores `reporter_id` on each issue, so one reporter can have many issues.

## Postman

Import `postman_collection.json` into Postman. With the local server running and empty `issues.json` and `reporters.json` files, run the collection to exercise the success and failure cases:

```powershell
postman collection run .\postman_collection.json --verbose --no-report-events
```

The collection includes assertions for response status and key response fields. The two desktop captures below show a successful issue creation and a title validation error.

### Successful issue creation (201)

![Postman Desktop success response](postman_screenshots/create_issue_success.png)

### Validation failure (400)

![Postman Desktop validation failure response](postman_screenshots/create_issue_failure.png)

## Design decision

This exercise uses JSON files instead of a database because the brief asks for file-backed storage and the data set is small. Writes use a temporary file and atomic replacement to avoid leaving a partially-written JSON file if a process stops during a save. For a production service with concurrent writes, a database would be a better fit.
