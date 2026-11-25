# dbt-cube-ai-demo

**DataTLV 2026** live demo — *"Why English-to-SQL Usually Fails"*

A full semantic layer stack: **dbt v2 (Fusion) + DuckDB + Cube.js + Milvus RAG + AI Chat**, showing how a semantic layer turns vague natural-language questions into precise, governed SQL.

## Quick start

```bash
cp .env.example .env   # fill in AWS credentials + LLM_MODEL_ID
just all               # starts the full stack
just open              # opens all UIs in Chrome
```

| UI | URL | Password |
|----|-----|----------|
| AI Chat (Streamlit) | http://localhost:8501 | `test` |
| Cube Playground | http://localhost:4000 | — |
| Superset | http://localhost:8088 | admin / admin |
| dbt Docs | http://localhost:8082 | — |
| Milvus UI (Attu) | http://localhost:8003 | — |

## Demo script — AI Chat

Open the chat at **http://localhost:8501** and try these questions in order.

### Simple factual

```
Which courses have the lowest pass rate?
What is the average GPA by department?
```

### Bar charts

```
Show me a bar chart of average GPA by department, sorted descending.
Visualize student engagement score by course.
Which instructors teach the highest-performing sections? Show as a chart.
```

### Trends (line charts)

```
How has total enrollment changed over the last 4 semesters? Show as a line chart.
Which semester had the highest Dean's List rate? Plot it.
Show me the academic probation count trend over time.
```

### Attendance domain

```
What is the chronic absence rate by school? Show as a bar chart.
Which schools have attendance below 90%?
How many tardy days were recorded in the last semester?
```

### Cross-domain joins (two cubes at once)

```
Compare average GPA and attendance rate by academic year on the same chart.
Is there a correlation between attendance rate and GPA? Show me both metrics by semester.
```

### The talk's key demo moment

```
What is the Academic Performance Index trend over time?
```

A plain LLM hallucinates a column. Cube routes it through the semantic layer and answers correctly.

## Incremental commands

```bash
just dbt              # re-run dbt models
just sync             # dbt → Cube full sync
just dbt-to-cube      # re-sync manifest → Cube schemas only
just cube-to-superset # push Cube schemas → Superset datasets
just cube-to-rag      # ingest changed schemas into Milvus
just reset            # wipe all volumes and start fresh
```
