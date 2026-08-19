FROM ghcr.io/home-assistant/base:latest

ARG TARGETARCH
WORKDIR /usr/src/app

# Download and install Loophole CLI - choose correct asset for target arch
RUN apk add --no-cache curl && \
        mkdir -p /tmp/loophole && \
        case "${TARGETARCH}" in \
            x86_64|amd64) LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_64bit.tar.gz";; \
            aarch64|arm64) LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_arm64.tar.gz";; \
            *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
        esac && \
        echo "Downloading Loophole from: $LOOPHOLE_URL" && \
        curl -fsSL "${LOOPHOLE_URL}" -o /tmp/loophole.tar.gz && \
        tar -xzf /tmp/loophole.tar.gz -C /tmp/loophole --strip-components=1 && \
        ls /tmp/loophole && \
        mv /tmp/loophole/loophole /usr/local/bin/loophole && \
        chmod +x /usr/local/bin/loophole && \
        rm -rf /tmp/loophole*

COPY run.py ./

RUN chmod +x /usr/src/app/run.py

CMD ["python", "/usr/src/app/run.py"]
