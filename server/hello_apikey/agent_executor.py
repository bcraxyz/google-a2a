import os
import random
from typing import List

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

_VALID_TOKEN: str = os.environ.get("AGENT_API_TOKEN", "")
if not _VALID_TOKEN:
    raise RuntimeError("AGENT_API_TOKEN environment variable is not set.")

def say_hello() -> str:
    """Greets the user in a piratey slang."""
    return "Ahoy, matey! Welcome aboard, ye scallywag! 🏴‍☠️"

def roll_dice(n_dice: int) -> List[int]:
    """Rolls n_dice 6-sided dice and returns the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

def _get_valid_token() -> str:
    token = os.environ.get("AGENT_API_TOKEN")
    if not token:
        raise RuntimeError("AGENT_API_TOKEN environment variable is not set.")
    return token

class HelloAgentExecutor(AgentExecutor):
    """Public hello skill + authenticated roll_dice skill (API token auth)."""
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Pull the raw user text from the first text part of the message.
        user_text = ""
        if context.message and context.message.parts:
            for part in context.message.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    user_text = part.root.text.strip().lower()
                    break

        if len(user_text) > 500:
            await event_queue.enqueue_event(
                new_agent_text_message("❌ Input too long.")
            )
            return
        
        if user_text.startswith("roll"):
            auth_header: str = (context.request_metadata or {}).get("authorization", "")
            token = auth_header.removeprefix("Bearer ").strip()

            if not token or token != _VALID_TOKEN:
                await event_queue.enqueue_event(
                    new_agent_text_message("❌ Unauthorized: valid Bearer token required.")
                )
                return

            parts = user_text.split()
            try:
                n_dice = max(1, min(int(parts[1]), 20)) if len(parts) > 1 else 1
            except (ValueError, IndexError):
                n_dice = 1

            results = roll_dice(n_dice)
            await event_queue.enqueue_event(
                new_agent_text_message(f"🎲 Rolled {n_dice} dice → {results}")
            )
            return

        await event_queue.enqueue_event(new_agent_text_message(say_hello()))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")
