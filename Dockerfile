FROM ros:jazzy-ros-base-noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY scripts/ /app/scripts/

ENV PYTHONUNBUFFERED=1
ENV MPLCONFIGDIR=/tmp/matplotlib
