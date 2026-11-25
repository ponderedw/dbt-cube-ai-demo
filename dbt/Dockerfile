FROM python:3.11-slim

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install dbt Fusion (dbt v2)
RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update

ENV PATH="/root/.local/bin:$PATH"

# Pin duckdb to 1.x — dbt Fusion 2.0.x reads storage formats v64-v68 (DuckDB 1.x);
# DuckDB 2.0 writes v999 which dbt Fusion cannot read.
RUN pip install --no-cache-dir "duckdb>=1.1,<2.0"

WORKDIR /dbt

COPY . .

ENV DBT_PROFILES_DIR=/dbt

ENTRYPOINT ["/dbt/entrypoint.sh"]
