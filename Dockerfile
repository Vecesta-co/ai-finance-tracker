FROM python:3.11-slim

LABEL maintainer="vecesta.co@gmail.com"
LABEL description="AI Finance Tracker — Local-first personal finance tracker by Vecesta.co"

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
COPY fixtures/ ./fixtures/

RUN pip install --no-cache-dir -e .

EXPOSE 5000

ENTRYPOINT ["ai-finance-tracker"]
CMD ["serve", "--port", "5000", "--host", "0.0.0.0"]
