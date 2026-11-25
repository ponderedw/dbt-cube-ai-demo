{{ config(materialized='table') }}

select
    range::date as date_day
from
    range(
        date '2000-01-01',
        date '2030-12-31',
        interval '1 day'
    )