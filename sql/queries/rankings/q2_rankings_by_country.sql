SELECT
    c.competitor_id,
    c.name,
    c.country,
    c.country_code,
    cr.rank,
    cr.points,
    cr.movement,
    cr.competitions_played
FROM competitor_rankings cr
JOIN competitors c
    ON cr.competitor_id = c.competitor_id
WHERE LOWER(c.country) = LOWER(:country_name)
ORDER BY cr.rank ASC;