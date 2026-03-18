import os
import httpx
import asyncio
import logging
import warnings
import streamlit as st

from uuid import uuid4
from dotenv import load_dotenv
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from a2a.utils.constants import EXTENDED_AGENT_CARD_PATH

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("a2a").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="A2A Chatbot", page_icon="💬", initial_sidebar_state="auto")

def extract_text(resp) -> str:
    try:
        for part in resp.root.result.parts:
            root = getattr(part, "root", part)
            if hasattr(root, "text"):
                return root.text
    except Exception:
        pass
    return str(resp.model_dump(mode="json", exclude_none=True))

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

async def fetch_cards(url: str, token: str | None):
    async with httpx.AsyncClient() as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=url)
        public_card = await resolver.get_agent_card()
        extended_card = None
        if token and public_card.supports_authenticated_extended_card:
            extended_card = await resolver.get_agent_card(
                relative_card_path=EXTENDED_AGENT_CARD_PATH,
                http_kwargs={"headers": {"Authorization": f"Bearer {token}"}},
            )
        return public_card, extended_card

async def send_message(text: str, token: str | None) -> str:
    async with httpx.AsyncClient() as http:
        card = st.session_state.get("extended_card") or st.session_state.agent_card
        client = A2AClient(httpx_client=http, agent_card=card)
        resp = await client.send_message(make_request(text, token=token))
        return extract_text(resp)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "connected" not in st.session_state:
    st.session_state.connected = False
if "agent_card" not in st.session_state:
    st.session_state.agent_card = None
if "extended_card" not in st.session_state:
    st.session_state.extended_card = None

with st.sidebar:
    st.title("💬 A2A Chatbot")

    with st.expander("⚙️ Connection", expanded=True):
        server_url = st.text_input(
            "Agent URL",
            value=os.environ.get("AGENT_BASE_URL", "http://localhost:8080"),
        )
        enable_auth = st.checkbox("Enable Authentication", value=False)
        token_input = st.text_input(
            "Bearer Token",
            value=os.environ.get("AGENT_API_TOKEN", ""),
            type="password",
            disabled=not enable_auth,
        )

        col1, col2 = st.columns(2)
        with col1:
            connect_btn = st.button(
                "Connect",
                use_container_width=True,
                disabled=st.session_state.connected,
            )
        with col2:
            disconnect_btn = st.button(
                "Disconnect",
                use_container_width=True,
                disabled=not st.session_state.connected,
            )

    # Agent cards — shown only when connected
    if st.session_state.connected and st.session_state.agent_card:
        card = st.session_state.agent_card
        with st.expander("📋 Public Agent Card", expanded=True):
            st.caption(f"**{card.name}** `v{card.version}`")
            if card.description:
                st.caption(card.description)
            st.caption("**Skills**")
            for skill in card.skills or []:
                st.caption(f"- **{skill.name}**: {skill.description}")

        if st.session_state.extended_card:
            ext = st.session_state.extended_card
            with st.expander("🔐 Extended Agent Card", expanded=True):
                st.caption(f"**{ext.name}** `v{ext.version}`")
                if ext.description:
                    st.caption(ext.description)
                st.caption("**Skills**")
                for skill in ext.skills or []:
                    st.caption(f"- **{skill.name}**: {skill.description}")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if connect_btn:
    token = token_input if enable_auth else None
    with st.spinner("Connecting…"):
        try:
            public_card, extended_card = asyncio.run(fetch_cards(server_url, token))
            st.session_state.agent_card = public_card
            st.session_state.extended_card = extended_card
            st.session_state.connected = True
            st.session_state.messages = []
            st.rerun()
        except Exception as e:
            st.error(f"Could not connect: {e}")

if disconnect_btn:
    st.session_state.connected = False
    st.session_state.agent_card = None
    st.session_state.extended_card = None
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message…"):
    if not st.session_state.connected:
        st.warning("Enter the agent URL in the sidebar and click **Connect** to start chatting.")
    else:
        token = token_input if enable_auth else None

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    reply = asyncio.run(send_message(prompt, token))
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
