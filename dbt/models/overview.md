{% docs __overview__ %}

# Education Data — Semantic Layer Demo

This project powers the **DataTLV 2026** live demo: *"Why English-to-SQL Usually Fails"*.

Built with **dbt v2 (Fusion)** + **DuckDB** + **Cube.js** + **Milvus RAG**, it shows how a semantic layer turns vague natural-language questions into precise, governed SQL — without hallucinating columns or joining tables incorrectly.

---

## Semantic domains

| Domain | Model | Key metrics |
|--------|-------|-------------|
| Course Performance | `course_performance_summary` | Average GPA, Pass Rate, Engagement Score |
| Student Attendance | `student_attendance` | Attendance Rate, Absent Days, Tardy Days |
| Semester Trends | `semester_enrollment_trends` | Headcount, Dean's List, Probation Count |

Entities and measures are defined inline in `models.yml` using **dbt MetricFlow v2** format, then synced to Cube.js automatically via `dbt-cube-sync`.

---

## Questions to try in the AI Chat

> Open the Streamlit chat at **http://localhost:8501**

**Course performance**
- Which courses have the lowest pass rate this semester?
- Show me average GPA by department, sorted descending.
- What is the student engagement score for Computer Science?
- Which instructors teach the highest-performing sections?

**Attendance & absenteeism**
- What is the chronic absence rate by school?
- Which schools have attendance below 90%?
- How many tardy days (excluding ODP students) were recorded in Fall 2024?

**Enrollment & trends**
- How has total enrollment changed over the last 4 semesters?
- Which semester had the highest Dean's List rate?
- What percentage of students are currently on academic probation?

**Cross-domain (joins two cubes automatically)**
- Compare average GPA and attendance rate by academic year.
- What is the Academic Performance Index trend over time?

---

## How the pipeline works

```
Raw CSV seeds
    └─► dbt v2 (Fusion + DuckDB)   — 49 models, MetricFlow semantic layer
            └─► dbt-cube-sync       — generates Cube.js YAML from manifest
                    └─► Cube.js     — SQL API + Playground (port 4000)
                            └─► Milvus RAG + AI Chat (port 8501)
                            └─► Superset dashboards (port 8088)
                            └─► dbt Docs (port 8082)
```

To extend the semantic layer: add a measure to a model in `models.yml`, run `just sync`, and it is instantly queryable in natural language — no SQL changes needed.

{% enddocs %}
