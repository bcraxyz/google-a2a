FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./

RUN uv pip install --system .

COPY streamlit_app.py ./

ENV PORT=8080

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
