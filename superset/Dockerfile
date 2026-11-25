FROM apache/superset:latest

USER root

RUN uv pip install flask-cors psycopg2-binary

COPY superset_init.sh /app/superset_init.sh
RUN chmod +x /app/superset_init.sh

USER superset

ENTRYPOINT ["/app/superset_init.sh"]
