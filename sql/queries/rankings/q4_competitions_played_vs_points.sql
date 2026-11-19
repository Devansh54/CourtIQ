SELECT
    c.competitor_id,
    c.name,
    c.country,
    cr.competitions_played,
    cr.points,
    cr.rank
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
ORDER BY
    cr.competitions_played DESC,
    cr.points DESC;