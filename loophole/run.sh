#!/usr/bin/with-contenv bashio

# Dockerfile can not run run.py directly because of missing environment variables (SUPERVISOR_TOKEN).
# Dockerfile runs run.sh which fetches up the environment and then runs this script.

exec python3 /usr/src/app/run.py