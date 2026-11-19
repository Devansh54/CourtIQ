SELECT
    cr.rank,
    c.competitor_id,
    c.name,
    c.country,
    cr.movement,
    cr.points,
    cr.competitions_played
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
WHERE cr.movement > 0
ORDER BY
    cr.movement DESC,
    cr.rank ASC;