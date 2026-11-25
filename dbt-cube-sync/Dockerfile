FROM python:3.11-slim

RUN pip install "dbt-cube-sync>=0.1.0a56"

WORKDIR /workspace

ENTRYPOINT ["dbt-cube-sync"]
