
-- Q5: Find complexes containing more than one venue.

SELECT
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS total_venues
FROM complexes AS c
INNER JOIN venues AS v
    ON c.complex_id = v.complex_id
GROUP BY
    c.complex_id,
    c.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY
    total_venues DESC,
    c.complex_name;
