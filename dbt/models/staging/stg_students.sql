{{ config(materialized='view') }}

with source_data as (
    select
        student_id,
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        email,
        date_of_birth,
        enrollment_date,
        graduation_date,
        student_status,
        gpa,
        major_id,
        advisor_id,
        address_id,
        datediff('year', date_of_birth, current_date) as age,
        datediff('year', enrollment_date, current_date) as years_enrolled,
        case
            when gpa >= 3.5 then 'Dean''s List'
            when gpa >= 3.0 then 'Good Standing'
            when gpa >= 2.0 then 'Academic Warning'
            else 'Academic Probation'
        end as academic_standing,
        case
            when graduation_date is not null then 'Graduated'
            when student_status = 'active' and gpa >= 2.0 then 'Active'
            when student_status = 'active' and gpa < 2.0 then 'At Risk'
            else upper(left(student_status, 1)) || lower(substring(student_status, 2))
        end as current_status,
        created_at
    from {{ source('raw_edu', 'students') }}
)

select * from source_data