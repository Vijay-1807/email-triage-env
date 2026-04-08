FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
COPY --chown=user . $HOME/app

# If openenv-core provides a server, this will run it.
# As a fallback, we expose 7860 which HF Spaces expects.
EXPOSE 7860

# We need a long-running process that responds to HTTP port 7860.
# OpenEnv-core should handle this integration, if not, we assume standard usage.
# If running locally, you can use: python inference.py
# Start the OpenEnv server on port 7860
# Start the OpenEnv server as a module
CMD ["python", "-m", "server.app"]
