
-- Q2: Count the number of venues in each complex.

SELECT
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS total_venues
FROM complexes AS c
LEFT JOIN venues AS v
    ON c.complex_id = v.complex_id
GROUP BY
    c.complex_id,
    c.complex_name
ORDER BY
    total_venues DESC,
    c.complex_name;
