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
AGENT_API_TOKEN = os.environ.get("AGENT_API_TOKEN")
if not AGENT_API_TOKEN or not AGENT_BASE_URL:
    raise RuntimeError("Required environment variables are not set.")

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

def make_request(text: str) -> SendMessageRequest:
    return SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": uuid4().hex,
            },
            metadata={"Authorization": f"Bearer {AGENT_API_TOKEN}"},
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
        
        log.info("\n── Extended agent card (authenticated) ──")
        extended_card = await resolver.get_agent_card(
            relative_card_path=EXTENDED_AGENT_CARD_PATH,
            http_kwargs={"headers": {"Authorization": f"Bearer {AGENT_API_TOKEN}"}},
        )
        log.info(f"  Name:        {extended_card.name}")
        log.info("  Skills:")
        for skill in extended_card.skills:
            log.info(f"    • {skill.name}: {skill.description}")

        client = A2AClient(httpx_client=http, url=AGENT_BASE_URL)

        log.info("\n── Hello (no auth) ──")
        resp = await client.send_message(make_request("hello"))
        print(extract_text(resp))

        log.info("\n── Roll dice (with token) ──")
        resp = await client.send_message(make_request("roll 3"))
        print(extract_text(resp))

if __name__ == "__main__":
    asyncio.run(main())
