# FROM python:3.11.1-bullseye
FROM python@sha256:73e59efbf2b98694e53ddaccd16d62218b614e6970c7225d30bf9e7d1bf40076

RUN apt update \
    && apt -y install --no-install-recommends git-core vim \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
