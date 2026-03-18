# Google A2A

A collection of [A2A protocol](https://google.github.io/A2A/) agents and clients. Deploy on Google [Cloud Run](https://cloud.google.com/run) or [Railway](https://railway.app/?referralCode=alphasec).

## Structure

```
├── server/
│   └── hello/      # Public hello + authenticated dice-rolling agent
└── client/
    ├── streamlit_app.py    # Web GUI client
    └── hello_client.py      # CLI test client
```

## Quick Start

```bash
cp .env.example .env
# fill in AGENT_BASE_URL and AGENT_API_TOKEN
```

Run the server:
```bash
cd server/hello && uv run python __main__.py
```

Run the client:
```bash
cd client && streamlit run streamlit_app.py
```

## Servers

| Name | Path | Description |
|------|------|-------------|
| Hello | `server/hello` | Pirate greeting + authenticated dice rolling |

## Clients

| Name | Description |
|------|-------------|
| Streamlit GUI | Visual chat interface for any A2A-compliant agent |
| Hello test client | CLI script for quick smoke-testing |
