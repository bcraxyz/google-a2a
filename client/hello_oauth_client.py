"""
CLI test client for the hello_oauth server.
Fetches an OAuth token via client credentials flow, then calls both skills.
"""
import os
import httpx
import asyncio
import logging
import warnings

from uuid import uuid4
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from a2a.utils.constants import EXTENDED_AGENT_CARD_PATH
from dotenv import load_dotenv

load_dotenv()

AGENT_BASE_URL = os.environ.get("AGENT_BASE_URL")
OAUTH_ISSUER = os.environ.get("OAUTH_ISSUER")
OAUTH_AUDIENCE = os.environ.get("OAUTH_AUDIENCE")
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")

missing = [k for k, v in {
    "AGENT_BASE_URL": AGENT_BASE_URL,
    "OAUTH_ISSUER": OAUTH_ISSUER,
    "OAUTH_AUDIENCE": OAUTH_AUDIENCE,
    "OAUTH_CLIENT_ID": OAUTH_CLIENT_ID,
    "OAUTH_CLIENT_SECRET": OAUTH_CLIENT_SECRET,
}.items() if not v]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("a2a").setLevel(logging.WARNING)
log = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=DeprecationWarning)

def extract_text(resp) -> str:
    try:
        for part in resp.root.result.parts:
            root = getattr(part, "root", part)
            if hasattr(root, "text"):
                return root.text
    except Exception:
        pass
    return str(resp.model_dump(mode="json", exclude_none=True))

async def fetch_oauth_token() -> str:
    """Fetches an access token via OAuth 2.0 client credentials flow using OIDC discovery."""
    issuer = OAUTH_ISSUER.rstrip("/")
    async with httpx.AsyncClient() as http:
        discovery = await http.get(f"{issuer}/.well-known/openid-configuration")
        discovery.raise_for_status()
        token_url = discovery.json()["token_endpoint"]

        resp = await http.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "scope": f"{OAUTH_AUDIENCE}/.default",
            },
        )
        if not resp.is_success:
            raise RuntimeError(f"Token request failed ({resp.status_code}): {resp.text}")
        return resp.json()["access_token"]

def make_request(text: str, token: str | None = None) -> SendMessageRequest:
    metadata = {"Authorization": f"Bearer {token}"} if token else {}
    return SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": uuid4().hex,
            },
            metadata=metadata,
        ),
    )

async def main() -> None:
    async with httpx.AsyncClient() as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=AGENT_BASE_URL)

        log.info("── Public agent card ──")
        public_card = await resolver.get_agent_card()
        log.info(f"  Name:        {public_card.name}")
        log.info(f"  Description: {public_card.description}")
        log.info(f"  Version:     {public_card.version}")
        log.info("  Skills:")
        for skill in public_card.skills:
            log.info(f"    • {skill.name}: {skill.description}")

        log.info("\n── Fetching OAuth token ──")
        token = await fetch_oauth_token()
        log.info("  Token acquired.")

        log.info("\n── Extended agent card (authenticated) ──")
        extended_card = await resolver.get_agent_card(
            relative_card_path=EXTENDED_AGENT_CARD_PATH,
            http_kwargs={"headers": {"Authorization": f"Bearer {token}"}},
        )
        log.info(f"  Name:        {extended_card.name}")
        log.info("  Skills:")
        for skill in extended_card.skills:
            log.info(f"    • {skill.name}: {skill.description}")

        client = A2AClient(httpx_client=http, url=AGENT_BASE_URL)

        log.info("\n── Hello (no auth) ──")
        resp = await client.send_message(make_request("hello"))
        print(extract_text(resp))

        log.info("\n── Roll dice (with OAuth token) ──")
        resp = await client.send_message(make_request("roll 3", token=token))
        print(extract_text(resp))

if __name__ == "__main__":
    asyncio.run(main())
