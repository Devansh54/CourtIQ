SELECT
    cr.rank,
    c.competitor_id,
    c.name,
    c.country,
    c.country_code,
    cr.points,
    cr.movement,
    cr.competitions_played
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
ORDER BY
    cr.rank ASC,
    cr.points DESC
LIMIT 10;