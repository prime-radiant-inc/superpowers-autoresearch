# notes service

A tiny JSON API for storing short text notes, built on the Python standard
library only (`http.server`).

## Run

```bash
python3 server.py --port 8080
```

## Endpoints

| Method | Path         | Body               | Response                     |
|--------|--------------|--------------------|-------------------------------|
| GET    | `/notes`     | -                  | `{"notes": [...]}`            |
| POST   | `/notes`     | `{"text": "..."}`  | the created note              |
| GET    | `/notes/<id>`| -                  | the note, or 404              |
| DELETE | `/notes/<id>`| -                  | 204, or 404                   |

## Test

```bash
python3 -m unittest discover -s tests -t .
```
