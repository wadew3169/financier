FROM python:3.9-slim

LABEL maintainer="SecurityResearch"
LABEL description="Simulated Cryptocurrency Miner for Security Testing"
LABEL version="1.0"
LABEL purpose="SecurityTesting"

# Add non-root user
RUN useradd -m -s /bin/bash miner
WORKDIR /home/miner

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for Slack integration
RUN pip install --no-cache-dir requests

# Copy miner script
COPY fake_cryptominer.py /home/miner/
COPY entrypoint.sh /home/miner/

# Make scripts executable
RUN chmod +x /home/miner/fake_cryptominer.py
RUN chmod +x /home/miner/entrypoint.sh

# Create mining directory structure (similar to real miners)
RUN mkdir -p /home/miner/.mining/configs
RUN mkdir -p /home/miner/.mining/logs
RUN mkdir -p /home/miner/.mining/bins

# Create fake mining configuration
RUN echo '{"algo":"ethash","pool":"stratum+tcp://us1.ethermine.org:4444","wallet":"0x0000000000000000000000000000000000000000","threads":2}' > /home/miner/.mining/configs/config.json

# Create fake binary file to trigger AV/EDR
RUN echo "#!/bin/bash\n# XMRig Miner v6.16.2\n# Copyright (c) 2021-2023\n# OpenCL/CUDA Miner" > /home/miner/.mining/bins/xmrig
RUN chmod +x /home/miner/.mining/bins/xmrig

# Add some mining-related strings to trigger signature detection
RUN echo "stratum+tcp://pool.minexmr.com:4444\nstratum+tcp://gulf.moneroocean.stream:20128" > /home/miner/.mining/configs/pools.txt
RUN echo "randomx\nethash\nkawpow\nautolykos2" > /home/miner/.mining/configs/algos.txt

# Switch to non-root user
USER miner

# Set environment variables with defaults
ENV SLACK_WEBHOOK_URL=""
ENV BEACON_INTERVAL="30"
ENV ALGO="ethash"
ENV WALLET="0x0000000000000000000000000000000000000000"
ENV WORKER="dockerized-miner"
ENV THREADS="2"
ENV USE_GPU="false"
ENV INTENSITY="8"

ENTRYPOINT ["/home/miner/entrypoint.sh"]
