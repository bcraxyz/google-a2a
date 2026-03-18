# A2A Clients

Clients for interacting with any A2A-compliant agent.

## Setup

```
cd client
cp ../.env.example .env  # then fill in values
uv pip install -e .
```

## Streamlit Client

Visual chat interface with connect/disconnect, agent card inspection, and auth support.

```
streamlit run streamlit_app.py
```

Open `http://localhost:8501`, enter the agent URL, and click **Connect**.

## CLI Test Client (Hello)

CLI script that fetches both agent cards and runs a hello + dice-roll smoke test.

```
python hello_client.py
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `AGENT_BASE_URL` | URL of the A2A server to connect to |
| `AGENT_API_TOKEN` | Bearer token for authenticated skills |

Both can be set in `.env` or exported directly. The Streamlit GUI also accepts them via the sidebar at runtime.
