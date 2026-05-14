# Draft only — PE-OPS-CONTAINERS-02
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y ca-certificates curl python3 && rm -rf /var/lib/apt/lists/*

# Hermes source strategy: package-managed install during build, not host bind mount.
# Exact package/version to be pinned during implementation.

RUN useradd --create-home --shell /bin/bash elis-advisor
WORKDIR /workspace
USER elis-advisor
ENTRYPOINT ["/bin/bash"]
