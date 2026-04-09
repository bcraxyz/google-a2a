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
        error = resp.root.error
        if error:
            return f"⚠️ Server error: {error.message}"
    except Exception:
        pass
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

async def fetch_oauth_token(issuer: str, audience: str, client_id: str, client_secret: str) -> str:
    issuer = issuer.rstrip("/")
    async with httpx.AsyncClient() as http:
        discovery = await http.get(f"{issuer}/.well-known/openid-configuration")
        discovery.raise_for_status()
        token_url = discovery.json()["token_endpoint"]

        resp = await http.post(
            token_url,
            json={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": audience,              # Auth0
                "scope": f"{audience}/.default",   # Entra
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

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
if "active_token" not in st.session_state:
    st.session_state.active_token = None
if "last_auth_method" not in st.session_state:
    st.session_state.last_auth_method = "None"

with st.sidebar:
    st.title("💬 A2A Chatbot")

    with st.expander("⚙️ Connection", expanded=True):
        server_url = st.text_input(
            "Agent URL",
            value=os.environ.get("AGENT_BASE_URL", "http://localhost:8080"),
        )

        auth_method = st.selectbox(
            "Authentication Method",
            ["None", "API Token", "OAuth 2.0"],
        )

        # Disconnect if auth method changes while connected
        if auth_method != st.session_state.last_auth_method:
            st.session_state.last_auth_method = auth_method
            if st.session_state.connected:
                st.session_state.connected = False
                st.session_state.agent_card = None
                st.session_state.extended_card = None
                st.session_state.active_token = None
                st.session_state.messages = []
        
        # API Token fields
        if auth_method == "API Token":
            api_token = st.text_input(
                "Bearer Token",
                value=os.environ.get("AGENT_API_TOKEN", ""),
                type="password",
            )
        else:
            api_token = None
 
        # OAuth fields
        if auth_method == "OAuth 2.0":
            oauth_issuer = st.text_input(
                "Issuer URL",
                value=os.environ.get("OAUTH_ISSUER", ""),
                placeholder="https://your-tenant.auth0.com",
            )
            oauth_audience = st.text_input(
                "Audience",
                value=os.environ.get("OAUTH_AUDIENCE", ""),
                placeholder="https://your-agent-url",
            )
            oauth_client_id = st.text_input(
                "Client ID",
                value=os.environ.get("OAUTH_CLIENT_ID", ""),
            )
            oauth_client_secret = st.text_input(
                "Client Secret",
                value=os.environ.get("OAUTH_CLIENT_SECRET", ""),
                type="password",
            )
        else:
            oauth_issuer = oauth_audience = oauth_client_id = oauth_client_secret = None

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
    with st.spinner("Connecting…"):
        try:
            token = None
 
            if auth_method == "API Token":
                token = api_token or None
 
            elif auth_method == "OAuth 2.0":
                missing = [k for k, v in {
                    "Issuer URL": oauth_issuer,
                    "Audience": oauth_audience,
                    "Client ID": oauth_client_id,
                    "Client Secret": oauth_client_secret,
                }.items() if not v]
                if missing:
                    st.error(f"Missing OAuth fields: {', '.join(missing)}")
                    st.stop()
                token = asyncio.run(
                    fetch_oauth_token(oauth_issuer, oauth_audience, oauth_client_id, oauth_client_secret)
                )
                
            public_card, extended_card = asyncio.run(fetch_cards(server_url, token))
            st.session_state.agent_card = public_card
            st.session_state.extended_card = extended_card
            st.session_state.active_token = token
            st.session_state.connected = True
            st.session_state.messages = []
            st.rerun()
        except Exception as e:
            st.error(f"Could not connect: {e}")

if disconnect_btn:
    st.session_state.connected = False
    st.session_state.agent_card = None
    st.session_state.extended_card = None
    st.session_state.active_token = None
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message…"):
    if not st.session_state.connected:
        st.warning("Provide the agent URL in the sidebar and click **Connect** to start chatting.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    reply = asyncio.run(
                        send_message(prompt, st.session_state.active_token)
                    )
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
