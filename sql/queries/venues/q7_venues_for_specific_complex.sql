
-- Q7: Find venues belonging to a specific complex.
-- Example parameter: complex_pattern = '%Nacional%'

SELECT
    c.complex_id,
    c.complex_name,
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone
FROM complexes AS c
INNER JOIN venues AS v
    ON c.complex_id = v.complex_id
WHERE LOWER(c.complex_name) LIKE LOWER(:complex_pattern)
ORDER BY
    c.complex_name,
    v.venue_name;
