# Hello A2A Agent (API Key)

Simple A2A agent with two skills: a public greeting and an authenticated dice roller.

## Skills

| Skill | Auth required | Example |
|-------|--------------|---------|
| Hello | No | `hi`, `hello` |
| Roll Dice | Yes (Bearer token) | `roll 3`, `roll 5 dice` |

## Run Locally

```bash
cd server/hello_apikey
cp .env.example .env
uv run python __main__.py
```

Agent card: `http://localhost:8080/.well-known/agent.json`

## Deploy to [Railway](https://railway.app/?referralCode=alphasec)

1. Set root directory to `server/hello_apikey`
2. Add environment variables (see below)
3. Railway detects the `Dockerfile` and builds automatically

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_BASE_URL` | Yes | Public URL of this server (used in agent card) |
| `AGENT_API_TOKEN` | Yes | Static Bearer token for authenticated skills |
| `PORT` | No | Port to listen on (default: `8080`, injected automatically by Railway) |
