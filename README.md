# AI Chat Front-End

This project provides a minimal React-based front-end for an AI chat application.

## Running

Open `index.html` in a modern browser. The interface sends user messages to `/api/chat` via `POST` and expects a JSON response like:

```json
{"reply": "Hello there"}
```

No build step is required because React and Babel are loaded from CDNs.
