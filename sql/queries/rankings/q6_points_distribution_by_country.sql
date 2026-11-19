SELECT
    c.country,
    c.country_code,
    COUNT(DISTINCT c.competitor_id) AS total_competitors,
    SUM(cr.points) AS total_points,
    ROUND(AVG(cr.points), 2) AS average_points
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
GROUP BY
    c.country,
    c.country_code
ORDER BY
    total_points DESC;