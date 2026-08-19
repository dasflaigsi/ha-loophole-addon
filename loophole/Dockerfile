FROM ghcr.io/home-assistant/base:latest

WORKDIR /usr/src/app
ENV DATA_DIR=/data

# Download and install Loophole CLI
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tmp/loophole && cd /tmp/loophole && \
    curl -s https://api.github.com/repos/loophole/cli/releases/64816263 | grep -o '"browser_download_url": "[^"]*linux_64bit[^"]*"' | head -1 | cut -d'"' -f4 > /tmp/loophole_url.txt && \
    LOOPHOLE_URL=$(cat /tmp/loophole_url.txt) && \
    if [ -z "$LOOPHOLE_URL" ]; then LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_64bit.tar.gz"; fi && \
    echo "Downloading Loophole from: $LOOPHOLE_URL" && \
    curl -sL "$LOOPHOLE_URL" | tar xz --strip-components=1 && \
    ls && \
    mv loophole /usr/local/bin/loophole && chmod +x /usr/local/bin/loophole && \
    rm -rf /tmp/loophole*

COPY run.py ./

RUN chmod +x /usr/src/app/run.py

CMD ["python", "/usr/src/app/run.py"]
