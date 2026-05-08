# ELIS GitHub Agent Container
#
# Provides a containerised runtime for the ELIS GitHub Agent.
# - Runs as non-root user elis-github (UID 995, GID 983)
# - Loads GH_TOKEN from a read-only mounted secrets file
# - Only approves allowed verbs via the entrypoint gate
# - No Docker socket access; no host GitHub credentials leaked
#
# Build:
#   docker build -t elis-github-agent .
#
# Run (via compose, recommended):
#   docker compose -f ops/containers/github-agent/docker-compose.github-agent.yml run --rm elis-github-agent --check-only
#
# Labels:
#   org.opencontainers.image.title       = "ELIS GitHub Agent"
#   org.opencontainers.image.description = "Containerised GitHub Agent runtime for ELIS — elis-git-bot identity"
#   org.opencontainers.image.source      = "https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform"
#   org.opencontainers.image.authors     = "ELIS Infrastructure"
#   org.opencontainers.image.version     = "1.0.0"

FROM ubuntu:24.04

LABEL org.opencontainers.image.title="ELIS GitHub Agent"
LABEL org.opencontainers.image.description="Containerised GitHub Agent runtime for ELIS — elis-git-bot identity"
LABEL org.opencontainers.image.source="https://github.com/rochasamurai/ELIS-Multi-AI-Agent-Platform"
LABEL org.opencontainers.image.authors="ELIS Infrastructure"
LABEL org.opencontainers.image.version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        ca-certificates \
        jq \
        bash \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        | tee /etc/apt/sources.list.d/github-cli.list >/dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

ARG UID=995
ARG GID=983
ARG SECRETS_GID=982

# elis-github is the primary user (matches host UID 995).
# Supplementary group SECRETS_GID (982, elis-github-secrets on host)
# grants read access to the mounted secret file.
RUN groupadd -g ${GID} elis-github && \
    groupadd -g ${SECRETS_GID} elis-github-secrets && \
    useradd -m -u ${UID} -g ${GID} -G ${SECRETS_GID} -s /bin/bash elis-github

WORKDIR /workspace

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh

USER elis-github

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]