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
  --set-env-vars AGENT_BASE_URL=https://your-service-url,OAUTH_ISSUER=https://sts.windows.net/your-tenant-id/,OAUTH_AUDIENCE=your-client-id
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_BASE_URL` | Yes | Public URL of this server (used in agent card) |
| `OAUTH_ISSUER` | Yes | OAuth issuer URL — for Entra use `https://sts.windows.net/your-tenant-id/` (with trailing slash) |
| `OAUTH_AUDIENCE` | Yes | OAuth audience — for Entra this is the Application (client) ID |
| `PORT` | No | Port to listen on (default: `8080`, injected automatically by Cloud Run/Railway) |

## OAuth Provider Setup

**Auth0:** Create an API with your `AGENT_BASE_URL` as the identifier. Use the auto-created Machine-to-Machine app for `client_id` and `client_secret`.

**Entra (Azure AD):** Register an app and expose an API (set an Application ID URI under **Expose an API**). Set `OAUTH_AUDIENCE` to the Application (client) ID. Grant admin consent for the app's own API permissions. When connecting via the Streamlit client, use `https://login.microsoftonline.com/your-tenant-id/v2.0` as the issuer and `openid profile email offline_access your-client-id/.default` as the scope — the v2.0 endpoint is required for the scope parameter to be respected.
