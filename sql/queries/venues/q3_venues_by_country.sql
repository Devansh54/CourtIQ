
-- Q3: Display venues belonging to a specific country.
-- Example parameter: country_name = 'Chile'

SELECT
    venue_id,
    venue_name,
    city_name,
    country_name,
    country_code,
    timezone,
    complex_id
FROM venues
WHERE LOWER(country_name) = LOWER(:country_name)
ORDER BY city_name, venue_name;
