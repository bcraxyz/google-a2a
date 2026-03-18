# Hello A2A Server

Simple A2A server with two skills: a public greeting and an authenticated dice roller.

## Skills

| Skill | Auth required | Example |
|-------|--------------|---------|
| Hello | No | `hi`, `hello` |
| Roll Dice | Yes (Bearer token) | `roll 3`, `roll 5 dice` |

## Run Locally

```bash
cd server/hello
cp ../../.env.example .env  # then fill in values
uv run python __main__.py
```

Agent card available at `http://localhost:8080/.well-known/agent.json`.

## Deploy to [Railway](https://railway.app/?referralCode=alphasec)

1. Set root directory to `server/hello` in Railway service settings
2. Add environment variables: `AGENT_API_TOKEN`, `AGENT_BASE_URL`
3. Railway detects the `Dockerfile` and builds automatically

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_API_TOKEN` | Yes | Bearer token for authenticated skills |
| `AGENT_BASE_URL` | Yes | Public URL of this server (used in agent card) |
| `PORT` | No | Port to listen on (default: `8080`, set automatically by Railway) |
