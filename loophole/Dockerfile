FROM ghcr.io/home-assistant/base:latest

ARG BUILD_ARCH
WORKDIR /usr/src/app

# Set environment variables, is used in run.py
ENV DATA_DIR=/data

# Download and install Loophole CLI - choose correct asset for target arch
RUN apk add --no-cache \
        curl \
        python3 \
        tar && \
    mkdir -p /tmp/loophole && \
    case "${BUILD_ARCH}" in \
        x86_64|amd64) LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_64bit.tar.gz";; \
        aarch64|arm64) LOOPHOLE_URL="https://github.com/loophole/cli/releases/download/1.0.0-beta.15/loophole-cli_1.0.0-beta.15_linux_arm64.tar.gz";; \
        *) echo "Unsupported architecture: ${BUILD_ARCH}" && exit 1 ;; \
    esac && \
    echo "Downloading Loophole from: $LOOPHOLE_URL" && \
    curl -fsSL "${LOOPHOLE_URL}" -o /tmp/loophole.tar.gz && \
    tar -xzf /tmp/loophole.tar.gz -C /tmp/loophole --strip-components=1 && \
    ls /tmp/loophole && \
    mv /tmp/loophole/loophole /usr/local/bin/loophole && \
    chmod +x /usr/local/bin/loophole && \
    rm -rf /tmp/loophole*

# Verify installation
RUN \
    echo "=== Loophole installation ===" && \
    ls -lah /usr/local/bin/loophole && \
    /usr/local/bin/loophole --version && \
    echo "=== PATH ===" && \
    echo "${PATH}" && \
    which loophole


RUN chmod +x /usr/src/app/run.py

CMD ["python3", "/usr/src/app/run.py"]
