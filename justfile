# dbt-cube-ai-demo  –  DataTLV 2026 live demo
#
# Prerequisites:
#   - Docker Desktop running
#   - cp .env.example .env  (fill in ANTHROPIC_API_KEY or OPENAI_API_KEY)

# Start the full stack (semantic layer + AI chat)
all:
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.ai.yml \
        -f docker-compose.ui.yml \
        up --build

# Start only the semantic layer (dbt + Cube + Superset) — no AI
sl:
    docker compose -f docker-compose.yml up --build

# Start in detached mode
up:
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.ai.yml \
        -f docker-compose.ui.yml \
        up -d

# Stop everything
down:
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.ai.yml \
        -f docker-compose.ui.yml \
        down

# Follow logs
logs:
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.ai.yml \
        -f docker-compose.ui.yml \
        logs -f

# Open all UIs in Chrome
open:
    open -a "Google Chrome" \
        "http://localhost:4000" \
        "http://localhost:8082" \
        "http://localhost:8088" \
        "http://localhost:8501" \
        "http://localhost:8003"

# Reset everything (removes volumes)
reset:
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.ai.yml \
        -f docker-compose.ui.yml \
        down -v

# Run only dbt (re-build models + sync to Cube)
dbt:
    docker compose -f docker-compose.yml run --rm dbt

# Re-run the full dbt → Cube sync after changing metrics YAML
sync:
    docker compose -f docker-compose.yml run --rm dbt-cube-sync

# Incremental: re-sync dbt manifest → Cube schemas (skips dbt run)
dbt-to-cube:
    docker compose -f docker-compose.yml run --rm \
        dbt-cube-sync \
        dbt-to-cube \
            --manifest /workspace/dbt/target/manifest.json \
            --catalog  /workspace/dbt/target/catalog.json \
            --output   /workspace/cube_output

# Incremental: sync Cube schemas → Superset datasets (via dbt-cube-sync cube-to-bi)
cube-to-superset:
    docker compose -f docker-compose.yml run --rm --no-deps cube-to-superset

# Incremental: ingest updated Cube schemas into Milvus (only changed cubes)
cube-to-rag:
    curl -s -X POST http://localhost:8081/embeddings/ingest \
        -H 'Content-Type: application/json' \
        -d '{"force_full": false}' | python3 -m json.tool

# Start a local Coder server (requires: curl -L https://coder.com/install.sh | sh)
coder:
    coder server --access-url http://localhost:3000 --wildcard-access-url "*.localhost:3000"
