{{ config(materialized='table', schema='marts') }}

{{
  dbt_simple_metrics.metrics(
    'course_performance_summary',
    ['department_name', 'semester_name', 'academic_year', 'performance_category'],
    ['average_course_gpa', 'total_course_enrollments', 'course_pass_rate']
  )
}}
