FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1 \
    PROMPT_BUCKET=restaurant-booking-prompts \
    PROMPT_VERSION=1.0.0



COPY requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt




RUN uv pip install aws-opentelemetry-distro==0.12.2

# Copy files BEFORE switching user
COPY . .

# Create non-root user and set ownership
RUN useradd -m -u 1000 bedrock_agentcore && \
    chown -R bedrock_agentcore:bedrock_agentcore /app

USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

CMD ["python", "-m", "src.workflows.restaurant_workflow"]
