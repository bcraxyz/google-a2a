# A2A Clients

Clients for interacting with any A2A-compliant agent.

## Setup

```
cd client
cp .env.example .env  # then fill in values
uv pip install -e .
```

## Streamlit Client

Visual chat interface with connect/disconnect, agent card inspection, and auth support.

```
streamlit run streamlit_app.py
```

Open `http://localhost:8501`, enter the agent URL, and click **Connect**.

## CLI Test Client (API Key)
```
python hello_apikey_client.py
```

## CLI Test Client (OAuth 2.0)
```
python hello_oauth_client.py
````
