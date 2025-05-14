FROM cassandra:4.1

# copy your init script
COPY cassandra-init.sh /docker-entrypoint-initdb.d/

# copy our wrapper
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# make both executable
RUN chmod +x /docker-entrypoint-initdb.d/cassandra-init.sh \
             /usr/local/bin/entrypoint.sh

# use the wrapper as ENTRYPOINT
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cassandra", "-f"]
