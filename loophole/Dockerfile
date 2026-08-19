FROM ghcr.io/home-assistant/base:latest

ARG TARGETARCH
WORKDIR /usr/src/app
ENV DATA_DIR=/data

# Download and install Loophole CLI - choose correct asset for target arch
RUN apk add --no-cache curl && \
        mkdir -p /tmp/loophole && cd /tmp/loophole && \
        case "${TARGETARCH}" in \
            x86_64|amd64) ASSET_PATTERN="linux_64bit";; \
            aarch64|arm64) ASSET_PATTERN="linux_arm64";; \
            *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
        esac && \
        # Try to discover a matching release asset; fall back to linux_64bit and a pinned URL
        LOOPHOLE_URL=$(curl -s https://api.github.com/repos/loophole/cli/releases/64816263 | grep -o '"browser_download_url": "[^"]*'"$ASSET_PATTERN"'[^"]*"' | head -1 | cut -d'"' -f4) && \
        if [ -z "$LOOPHOLE_URL" ]; then \
            echo "Loophole release not found for architecture: ${TARGETARCH}. Taking fallback: linux_64bit" ; \
            LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_64bit.tar.gz" ; \
        fi && \
        echo "Downloading Loophole from: $LOOPHOLE_URL" && \
        curl -sL "$LOOPHOLE_URL" | tar xz --strip-components=1 && \
        ls && \
        mv loophole /usr/local/bin/loophole && chmod +x /usr/local/bin/loophole && \
        rm -rf /tmp/loophole*

COPY run.py ./

RUN chmod +x /usr/src/app/run.py

CMD ["python", "/usr/src/app/run.py"]
