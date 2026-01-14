FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir uv

WORKDIR /repo

ENTRYPOINT ["bash", "/repo/docker/ci_linux.sh"]
