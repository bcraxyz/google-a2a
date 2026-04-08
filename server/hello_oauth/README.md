# Hello A2A Agent (OAuth)

Simple A2A agent with two skills: a public greeting and an OAuth-authenticated dice roller.

## Skills

| Skill | Auth required | Example |
|-------|--------------|---------|
| Hello | No | `hi`, `hello` |
| Roll Dice | Yes (OAuth 2.0 Bearer token) | `roll 3`, `roll 5 dice` |

## Run Locally

```bash
cd server/hello_oauth
cp .env.example .env
uv run python __main__.py
```

Agent card: `http://localhost:8080/.well-known/agent.json`


## Deploy to [Railway](https://railway.app/?referralCode=alphasec)
 
1. Set root directory to `server/hello_oauth`
2. Add environment variables (see below)
3. Railway detects the `Dockerfile` and builds automatically


## Deploy to [Cloud Run](https://cloud.google.com/run)

```bash
gcloud run deploy hello-oauth \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_BASE_URL=https://your-service-url,OAUTH_ISSUER=https://your-tenant.auth0.com,OAUTH_AUDIENCE=https://your-agent-url
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_BASE_URL` | Yes | Public URL of this server (used in agent card) |
| `OAUTH_ISSUER` | Yes | OAuth provider base URL (e.g. `https://your-tenant.auth0.com`) |
| `OAUTH_AUDIENCE` | Yes | OAuth audience — for Entra this is the client ID |
| `PORT` | No | Port to listen on (default: `8080`, injected automatically by Cloud Run/Railway) |

## OAuth Provider Setup

**Auth0:** Create an API with your `AGENT_BASE_URL` as the identifier. Use the auto-created Machine-to-Machine app for `client_id` and `client_secret`.

**Entra (Azure AD):** Register an app. Set `OAUTH_AUDIENCE` to the Application (client) ID. Grant the M2M app the necessary API permissions.
