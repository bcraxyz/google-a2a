FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./

RUN uv pip install --system .

COPY __init__.py __main__.py agent_executor.py ./

ENV PORT=8080

CMD ["python", "__main__.py"]
