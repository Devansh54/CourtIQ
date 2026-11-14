
-- Q6: Group venues by country and count them.

SELECT
    country_name,
    country_code,
    COUNT(venue_id) AS total_venues,
    COUNT(DISTINCT city_name) AS total_cities,
    COUNT(DISTINCT timezone) AS total_timezones
FROM venues
GROUP BY
    country_name,
    country_code
ORDER BY
    total_venues DESC,
    country_name;
