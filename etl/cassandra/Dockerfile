FROM cassandra:4.1

# Copy initialization script
COPY cassandra-init.sh /docker-entrypoint-initdb.d/

# Make the script executable
RUN chmod +x /docker-entrypoint-initdb.d/cassandra-init.sh 