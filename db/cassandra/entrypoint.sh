#!/usr/bin/env bash
set -e

# 1) Launch the official Cassandra entrypoint in the background
docker-entrypoint.sh "$@" &
CASSANDRA_PID=$!

# 2) Wait for CQL (native transport) to come up on the Docker DNS name "cassandra"
echo "⏳ Waiting for Cassandra to become available…"
until cqlsh cassandra -u cassandra -p cassandra \
      -e "describe keyspaces" >/dev/null 2>&1; do
  sleep 2
done

# 3) Run your shell init script (which itself calls cqlsh -e "…")
echo "✅ Cassandra is ready — running init script"
/docker-entrypoint-initdb.d/cassandra-init.sh

# 4) Hand control back to Cassandra so it stays in the foreground
wait $CASSANDRA_PID
