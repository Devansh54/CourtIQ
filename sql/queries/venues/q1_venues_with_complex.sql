
-- Q1: Display all venues with their associated complex names.

SELECT
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_id,
    c.complex_name
FROM venues AS v
INNER JOIN complexes AS c
    ON v.complex_id = c.complex_id
ORDER BY
    c.complex_name,
    v.venue_name;
